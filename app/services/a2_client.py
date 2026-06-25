import json
import os
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
    token = state.get("token")
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
    return {
        "status_code": response.status_code,
        "ok": response.is_success and not errors,
        "a2_chat_url": chat_url,
        "payload": payload,
        "final_response": final_response,
        "events": events,
        "errors": errors,
        "raw_body": response.text if not events else None,
    }


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
