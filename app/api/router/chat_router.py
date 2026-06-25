from fastapi import APIRouter, Header
from app.schema.request import (
    ChatMessageRequest
)
from app.services.orchestration.orchestration import (
    Orchestrator
)
# from app.services.session.session_markdown_exporter import (
#     append_chat_turn
# )

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatMessageRequest,
    authorization: str = Header(None)
):

    return await (
        Orchestrator.handle_chat(
            request.message,
            request.session_id,
            authorization
        )
    )


# @router.post("/chat")
# async def chat(
#     request: ChatMessageRequest,
#     authorization: str = Header(None)
# ):
#     response = await Orchestrator.handle_chat(
#         request.message,
#         request.session_id,
#         authorization
#     )

#     # if isinstance(response, dict):
#     #     session_id = response.get(
#     #         "session_id",
#     #         request.session_id or "unknown-session"
#     #     )

#     #     # append_chat_turn(
#     #     #     session_id,
#     #     #     request.message,
#     #     #     response
#     #     # )

#     return response
