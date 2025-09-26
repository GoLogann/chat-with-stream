from __future__ import annotations
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    message_id: str
    chat_id: str
    user_id: str
    role: Literal["user", "assistant", "system"] = "user"
    content: str
    created_at: datetime


class Chat(BaseModel):
    chat_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_preview: Optional[str] = None


class ChatSession(BaseModel):
    session_id: str
    chat_id: str
    user_id: str
    status: Literal["active", "ended"] = "active"
    started_at: datetime
    ended_at: Optional[datetime] = None
    last_event_at: Optional[datetime] = None


class RawItem(BaseModel):
    PK: str
    SK: str
    GSI1PK: Optional[str] = None
    GSI1SK: Optional[str] = None
    GSI2PK: Optional[str] = None
    GSI2SK: Optional[str] = None
    GSI3PK: Optional[str] = None
    GSI3SK: Optional[str] = None
    GSI4PK: Optional[str] = None
    GSI4SK: Optional[str] = None
    type: Literal["USER","CHAT","MSG","SESSION"]
    data: Dict[str, Any] = Field(default_factory=dict)