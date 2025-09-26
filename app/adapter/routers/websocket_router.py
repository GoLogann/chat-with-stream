# app/adapter/api/websocket.py

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from dependency_injector.wiring import inject, Provide

from app.adapter.schemas.chat import AskBody
from app.core.service.chat.chat_service import ChatService
from app.container import Container

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/chat/completions")
@inject
async def chat_endpoint(
    websocket: WebSocket,
    chat_service: ChatService = Depends(Provide[Container.chat_service]),
):
    await websocket.accept()
    last_active_session: dict | None = None
    user_id: str | None = None

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            payload = AskBody(**data)

            user_id = payload.user_id

            async for event in chat_service.ask_stream(
                user_id=payload.user_id,
                question=payload.question,
                chat_id=payload.chat_id or None,
                session_id=payload.session_id or None,
            ):
                if event.get("type") == "start":
                    last_active_session = {
                        "session_id": event.get("session_id"),
                        "user_id": user_id
                    }
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info(f"Cliente com user_id '{user_id}' desconectou do WS.")
        if last_active_session:
            sid = last_active_session["session_id"]
            uid = last_active_session["user_id"]
            logger.info(f"Tentando encerrar a sessão {sid} para o usuário {uid}.")
            try:
                chat_service.end_session(uid, sid)
                logger.info(f"Sessão encerrada com sucesso (disconnect): {sid}")
            except Exception:
                logger.exception(f"Falha ao encerrar sessão (disconnect): {sid}")

    except Exception as e:
        logger.exception("Erro inesperado no WS:")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        await websocket.close(code=1011, reason="Internal server error")