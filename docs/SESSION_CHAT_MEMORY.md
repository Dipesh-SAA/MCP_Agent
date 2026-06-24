# Session Chat Memory

This file documents what is stored in the in-memory session store for the chat workflow.

No application code is changed by this document.

## Active API

All chat requests go through one endpoint:

```text
POST /MCP_Agents/api/chat
```

Request body:

```json
{
  "session_id": "optional-existing-session-id",
  "message": "user message"
}
```

Optional header:

```text
Authorization: Bearer <token>
```

## Storage Location

Session state is stored in memory here:

```python
SESSIONS: Dict[str, dict] = {}
```

File:

```text
app/services/session/session_store.py
```

Important: this is process memory only. If the FastAPI server restarts, stored sessions are lost.

## Stored Session Shape

Each `session_id` maps to a dictionary like this:

```json
{
  "session_id": "uuid",
  "token": "Authorization header value",
  "user_input": "original user request",
  "requirements": "generated requirement text",
  "plan": {},
  "current_step": "chat | requirement_review | plan_review | completed",
  "output": "generated SQL or other output",
  "verified_output": "verification result",
  "api_response": {},
  "history": []
}
```

## Field Meanings

| Field | Purpose |
|---|---|
| `session_id` | Unique ID for continuing the same chat. |
| `token` | Authorization header saved for execution node calls. |
| `user_input` | Original workflow requirement from the user. |
| `requirements` | Output from the requirement agent. |
| `plan` | Output from the planner node. |
| `current_step` | Tracks where the session is in the workflow. |
| `output` | Generated code/output, such as SQL. |
| `verified_output` | Requirement verification result. |
| `api_response` | Response returned by the execution node. |
| `history` | Conversation messages saved for the session. |

## Current Workflow Steps

```text
chat
  -> workflow request
  -> requirement_review
  -> approve
  -> plan_review
  -> approve
  -> execution node
  -> completed
```

Modify/reject behavior:

```text
requirement_review + modify/reject -> requirement agent again
plan_review + modify/reject -> planner agent again
```

## Chat History Format

The `history` list stores messages like:

```json
[
  {
    "role": "user",
    "message": "hii can you help me"
  },
  {
    "role": "assistant",
    "message": "Hi, how can I help you?"
  }
]
```

## Markdown Export Template

Use this shape if you want to manually export one session to Markdown:

```md
# Chat Session Export

Session ID: `<session_id>`

Current Step: `<current_step>`

## User Input

<user_input>

## Requirements

<requirements>

## Plan

```json
<plan>
```

## Execution Response

```json
<api_response>
```

## Output

<output>

## Verification

<verified_output>

## Conversation History

### user

<message>

### assistant

<message>
```

## Notes

- The current app does not persist sessions to disk.
- A Markdown export endpoint is not implemented in the app.
- This document only describes the current in-memory session structure.
