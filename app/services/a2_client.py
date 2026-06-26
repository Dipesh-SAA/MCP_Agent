import json
import os
import re
from typing import Any

import httpx


DEFAULT_A2_CHAT_URL = "http://localhost:8000/api/chat"


class A2ClientError(RuntimeError):
    pass


def build_plan_review_payload(state: dict[str, Any]) -> dict[str, Any]:
    plan = state.get("plan")
    if not isinstance(plan, dict):
        raise A2ClientError("Cannot call A2 because approved plan is missing or invalid.")
    return {
        "session_id": state.get("session_id"),
        "type": "plan_review",
        "plan": plan,
    }


async def call_a2_with_plan(state: dict[str, Any]) -> dict[str, Any]:
    payload = build_plan_review_payload(state)
    chat_url = os.getenv("A2_CHAT_URL", DEFAULT_A2_CHAT_URL).strip() or DEFAULT_A2_CHAT_URL
    timeout_seconds = float(os.getenv("A2_TIMEOUT_SECONDS", "120"))
    headers = {}
    token = _authorization_header(state.get("token"))
    if token:
        headers["Authorization"] = token

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(
            chat_url,
            json={
                "message": json.dumps(payload),
                "session_id": state.get("session_id") or "default",
            },
            headers=headers,
        )

    events = _parse_sse_events(response.text)
    errors = [
        event.get("error") or event.get("content")
        for event in events
        if event.get("type") in {"error", "run_failed"} and (event.get("error") or event.get("content"))
    ]
    final_response = _final_response_from_events(events)
    response_error = _response_error(final_response)
    if response_error:
        errors.append(response_error)
    activity_log = _activity_log_from_events(events, final_response)
    return {
        "status_code": response.status_code,
        "ok": response.is_success and not errors,
        "payload": payload,
        "authorization_forwarded": bool(token),
        "final_response": final_response,
        "activity_log": activity_log,
        "events": events,
        "errors": errors,
        "raw_body": response.text if not events else None,
    }


def _authorization_header(token: Any) -> str | None:
    if not isinstance(token, str):
        return None
    value = token.strip()
    if not value:
        return None
    if value.lower().startswith("bearer "):
        return value
    return f"Bearer {value}"


def _response_error(final_response: str | None) -> str | None:
    if not final_response:
        return None
    lowered = final_response.lower()
    failure_markers = (
        "workflow paused",
        " error:",
        "authorization has been denied",
        "backend token context: missing",
        "token_expired",
        "run failed",
    )
    if any(marker in lowered for marker in failure_markers):
        return final_response
    return None


def _parse_sse_events(body: str) -> list[dict[str, Any]]:
    events = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data:
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def _final_response_from_events(events: list[dict[str, Any]]) -> str | None:
    content_parts = [
        str(event.get("content"))
        for event in events
        if event.get("type") in {"content", "content_delta"} and event.get("content")
    ]
    if content_parts:
        return "".join(content_parts)
    for event in reversed(events):
        if event.get("content"):
            return str(event["content"])
    return None


def _activity_log_from_events(events: list[dict[str, Any]], final_response: str | None) -> list[str]:
    lines: list[str] = []
    for event in events:
        event_type = event.get("type")
        content = _clean_text(event.get("content"))
        tool = _tool_label(event.get("tool"))
        metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}

        if event_type == "run_started":
            lines.append("Started A2 execution run.")
        elif event_type == "thinking" and content == "Loaded session context":
            lines.append("Loaded saved session context.")
        elif event_type == "thinking" and content == "ENTERING_WORKFLOW_ENGINE":
            protocol = metadata.get("input_protocol") or "workflow"
            lines.append(f"Entered A2 workflow engine using {protocol}.")
        elif event_type == "plan_created":
            tools = metadata.get("tools") if isinstance(metadata.get("tools"), list) else []
            if tools:
                lines.append(f"Prepared {len(tools)} MCP steps.")
                lines.extend(f"Queued {_tool_label(item)}." for item in tools[:40])
                if len(tools) > 40:
                    lines.append(f"Queued {len(tools) - 40} more MCP steps.")
            else:
                lines.append(content or "Prepared deterministic MCP plan.")
        elif event_type == "dependency_validated":
            missing = metadata.get("missing") if isinstance(metadata.get("missing"), list) else []
            if missing:
                lines.append(f"Checked arguments for {tool}; missing {', '.join(map(str, missing))}.")
            else:
                lines.append(f"Checked arguments for {tool}.")
        elif event_type in {"tool_started", "tool_call"}:
            lines.append(f"Started MCP tool {tool}.")
        elif event_type in {"tool_finished", "tool_result"}:
            lines.append(f"Finished MCP tool {tool}.")
        elif event_type == "tool_failed":
            error = _clean_text(event.get("error") or content)
            lines.append(f"MCP tool {tool} failed{': ' + error if error else '.'}")
        elif event_type == "state_updated":
            lines.append(f"Saved A2 workspace state after {tool}.")
        elif event_type == "recovery_started":
            lines.append(f"Paused for recovery after {tool}: {content}")
        elif event_type in {"error", "run_failed"}:
            error = _clean_text(event.get("error") or content)
            lines.append(error or "A2 reported an error.")
        elif event_type == "run_completed":
            lines.append("A2 run completed.")

    if final_response and _response_error(final_response):
        lines.append(_clean_text(final_response))

    return _dedupe(lines)


def _tool_label(value: Any) -> str:
    if not value:
        return "A2"
    text = str(value)
    if text.startswith("vibe."):
        text = text.removeprefix("vibe.")
    return text.replace("_", " ")


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"https?://\S+", "[hidden]", text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [hidden]", text, flags=re.IGNORECASE)
    text = re.sub(r"('a2_chat_url':\s*)'[^']+'", r"\1'[hidden]'", text)
    return text.strip()


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
