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
    used_sessions: set[str] = set()
    user_id: str | None = None

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            payload = AskBody(**data)

            user_id = payload.user_id  
            if payload.session_id:
                used_sessions.add(payload.session_id)

            async for event in chat_service.ask_stream(
                user_id=payload.user_id,
                question=payload.question,
                chat_id=payload.chat_id or None,
                session_id=payload.session_id or None,
            ):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("Cliente desconectou do WS; encerrando sessões associadas...")
        for sid in list(used_sessions):
            try:
                chat_service.end_session(user_id, sid)
                logger.info(f"Sessão encerrada (disconnect): {sid}")
            except Exception:
                logger.exception(f"Falha ao encerrar sessão (disconnect): {sid}")

    except Exception as e:
        logger.exception("Erro no WS:")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
