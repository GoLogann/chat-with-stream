from __future__ import annotations
from typing import AsyncIterator, Dict, Any

from app.core.service.llm.bedrock_service import BedrockChatService


class ChatService:
    def __init__(self, llm_service: BedrockChatService):
        self.llm_service = llm_service

    async def ask_stream(self, question: str, session_id: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Encaminha a pergunta para o LLM e devolve eventos de stream.
        """
        async for event in self.llm_service.generate_response_with_stream(
            prompt=question,
            session_id=session_id,
        ):
            yield event

    def end_session(self, session_id: str) -> None:
        """
        Encerra a sessão (limpa histórico) no serviço de LLM.
        """
        self.llm_service.end_session(session_id)