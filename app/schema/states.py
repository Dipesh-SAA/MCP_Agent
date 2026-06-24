from typing import Optional, TypedDict



# class AgentState(TypedDict):
#     user_input: str

#     requirements: Optional[str]

#     route: Optional[str]

#     html_requirements: Optional[str]

#     sql_requirements: Optional[str]
    

#     output: Optional[str]

#     html_output: Optional[str]

#     sql_output: Optional[str]

#     verified_output: Optional[str]

from typing import Optional, TypedDict


class AgentState(TypedDict):

    session_id: str

    user_input: str

    requirements: Optional[str]

    plan: Optional[str]

    current_step: Optional[str]








# class AgentState(TypedDict):

#     session_id: str

#     user_input: str

#     current_step: str

#     next_agent: Optional[str]

#     approval_required: bool

#     requirements: Optional[str]

#     route: Optional[str]

#     html_requirements: Optional[str]

#     sql_requirements: Optional[str]

#     output: Optional[str]

#     html_output: Optional[str]

#     sql_output: Optional[str]

#     verified_output: Optional[str]

#     conversation_history: List[dict]