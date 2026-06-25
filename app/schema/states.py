from typing import Any, Optional, TypedDict

class AgentState(TypedDict, total=False):

    session_id: str
    token: Optional[str]

    user_input: str

    requirements: Optional[str]
    plan: Optional[dict]

    current_step: Optional[str]

    modify_feedback: Optional[str]
    modify_target_step: Optional[str]

    route: Optional[str]

    output: Optional[str]
    verified_output: Optional[str]

    api_response: Optional[dict]

    history: list[dict[str, Any]]