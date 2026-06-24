from datetime import datetime
from pathlib import Path
from typing import Any


LOG_DIR = Path("docs/session_chats")


def _stringify_message(
    message: Any
) -> str:

    if hasattr(message, "type") and hasattr(message, "content"):
        return f"{message.type}: {message.content}"

    if hasattr(message, "content"):
        return str(message.content)

    return str(message)


def _stringify_messages(
    messages: Any
) -> str:

    if isinstance(messages, list):
        return "\n\n".join(
            _stringify_message(message)
            for message in messages
        )

    if hasattr(messages, "messages"):
        return _stringify_messages(
            messages.messages
        )

    return _stringify_message(
        messages
    )


def append_agent_chat(
    session_id: str,
    agent_name: str,
    prompt: Any,
    response: Any
):

    if not session_id:
        session_id = "unknown-session"

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = LOG_DIR / f"{session_id}.md"

    timestamp = datetime.utcnow().isoformat()

    content = f"""
## {agent_name}

Time: `{timestamp} UTC`

### Prompt

```text
{_stringify_messages(prompt)}
```

### Response

```text
{_stringify_message(response)}
```

---
"""

    with file_path.open(
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            content
        )
