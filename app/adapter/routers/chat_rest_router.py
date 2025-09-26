from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from app.adapter.schemas.chat import ChatListResponse, MessagesResponse, ChatSummary, SessionListResponse, UpdateTitlePayload
from app.core.service.chat.chat_service import ChatService
from app.container import Container

router = APIRouter(prefix="/api/chats", tags=["chats"])

@router.get("/{user_id}", response_model=ChatListResponse)
@inject
def list_chats(
    user_id: str, 
    limit: int = 20, 
    cursor: dict | None = None, 
    svc: ChatService = Depends(Provide[Container.chat_service])
):
    res = svc.list_chats(user_id=user_id, limit=limit, cursor=cursor)
    items = [
        ChatSummary(
            chat_id=i["chat_id"], 
            title=i["title"], 
            updated_at=i["updated_at"], 
            last_message_preview=i.get("last_message_preview")
        )
        for i in res["items"]
    ]
    return ChatListResponse(items=items, last_evaluated_key=res.get("last_evaluated_key"))


@router.get("/{chat_id}/messages", response_model=MessagesResponse)
@inject
def get_messages(
    chat_id: str, 
    limit: int = 100, 
    cursor: dict | None = None, 
    svc: ChatService = Depends(Provide[Container.chat_service])
):
    res = svc.history(chat_id=chat_id, limit=limit, cursor=cursor)
    items = [
        dict(
            message_id=i["message_id"], 
            role=i["role"], 
            content=i["content"], 
            created_at=i["created_at"]
        )
        for i in res["items"]
    ]
    return MessagesResponse(items=items, last_evaluated_key=res.get("last_evaluated_key"))


@router.get("/{chat_id}/sessions", response_model=SessionListResponse)
@inject
def list_sessions(
    chat_id: str, 
    limit: int = 50, 
    cursor: dict | None = None, 
    svc: ChatService = Depends(Provide[Container.chat_service])
):
    res = svc.list_sessions(chat_id=chat_id, limit=limit, cursor=cursor)
    return SessionListResponse(
        items=res["items"],
        last_evaluated_key=res.get("last_evaluated_key")
    )
    

@router.patch("/{user_id}/{chat_id}/title", status_code=status.HTTP_204_NO_CONTENT)
@inject
def update_chat_title(
    user_id: str,
    chat_id: str,
    payload: UpdateTitlePayload,
    svc: ChatService = Depends(Provide[Container.chat_service])
):
    svc.update_chat_title(
        user_id=user_id,
        chat_id=chat_id,
        new_title=payload.title
    )
    return