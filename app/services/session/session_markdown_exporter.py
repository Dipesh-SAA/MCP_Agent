import json
from datetime import datetime, timezone
from pathlib import Path


EXPORT_DIR = Path("docs/session_chats")


def _safe_session_id(
    session_id: str
):

    return "".join(
        char
        for char in session_id
        if char.isalnum() or char in [
            "-",
            "_"
        ]
    ) or "unknown-session"


def append_chat_turn(
    session_id: str,
    user_message: str,
    api_response: dict
):

    safe_session_id = _safe_session_id(
        session_id
    )

    EXPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = EXPORT_DIR / f"{safe_session_id}.md"
    is_new_file = not file_path.exists()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    with file_path.open(
        "a",
        encoding="utf-8"
    ) as file:
        if is_new_file:
            file.write(
                f"# Chat Session {session_id}\n\n"
            )

        file.write(
            f"## Turn - {timestamp}\n\n"
        )
        file.write(
            "### User Message\n\n"
        )
        file.write(
            f"{user_message}\n\n"
        )
        file.write(
            "### API Response\n\n"
        )
        file.write(
            "```json\n"
        )
        file.write(
            json.dumps(
                api_response,
                indent=2,
                default=str
            )
        )
        file.write(
            "\n```\n\n"
        )

    return file_path
