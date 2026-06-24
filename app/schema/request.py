from typing import Optional

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):

    session_id: Optional[str] = None

    message: str
