from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class AskBody(BaseModel):
    question: str
    user_id: str
    chat_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatSummary(BaseModel):
    chat_id: str
    title: str
    updated_at: str
    last_message_preview: Optional[str] = None


class ChatListResponse(BaseModel):
    items: List[ChatSummary]
    last_evaluated_key: Optional[dict] = None


class MessageDTO(BaseModel):
    message_id: str
    role: Literal["user","assistant","system"]
    content: str
    created_at: str


class MessagesResponse(BaseModel):
    items: List[MessageDTO]
    last_evaluated_key: Optional[dict] = None

class UpdateTitlePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)