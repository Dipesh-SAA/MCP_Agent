from typing import Dict


SESSIONS: Dict[str, dict] = {}


def save_state(
    session_id: str,
    state: dict
):
    SESSIONS[session_id] = state


def get_state(
    session_id: str
):
    return SESSIONS.get(session_id)


def update_state(
    session_id: str,
    updates: dict
):
    if session_id not in SESSIONS:
        return None

    SESSIONS[session_id].update(updates)

    return SESSIONS[session_id]


def delete_state(
    session_id: str
):
    if session_id in SESSIONS:
        del SESSIONS[session_id]


def session_exists(
    session_id: str
):
    return session_id in SESSIONS
