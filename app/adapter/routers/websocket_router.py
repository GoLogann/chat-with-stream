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

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)

            payload = AskBody(**data)
            used_sessions.add(payload.session_id)

            await websocket.send_json({"type": "start", "session_id": payload.session_id})

            async for event in chat_service.ask_stream(
                question=payload.question,
                session_id=payload.session_id,
            ):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("Cliente desconectou do WS; encerrando sessões associadas...")
        for sid in list(used_sessions):
            try:
                chat_service.end_session(sid)
                logger.info(f"Sessão encerrada (disconnect): {sid}")
            except Exception:
                logger.exception(f"Falha ao encerrar sessão (disconnect): {sid}")

    except Exception as e:
        logger.exception("Erro no WS:")
        for sid in list(used_sessions):
            try:
                chat_service.end_session(sid)
                logger.info(f"Sessão encerrada (erro): {sid}")
            except Exception:
                logger.exception(f"Falha ao encerrar sessão (erro): {sid}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
