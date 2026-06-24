from fastapi import APIRouter

from app.schema.request import (
    ChatMessageRequest
)
from app.services.orchestration.orchestration import (
    Orchestrator
)

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatMessageRequest
):

    return await (
        Orchestrator.handle_chat(
            request.message,
            request.session_id
        )
    )
