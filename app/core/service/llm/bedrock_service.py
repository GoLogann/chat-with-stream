from __future__ import annotations

import logging
from typing import AsyncIterator, Dict, Any

from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable

from app.core.config import Settings
from app.core.service.llm.base_langchain_service import BaseLangChainService

logger = logging.getLogger(__name__)


class BedrockChatService(BaseLangChainService):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not self.settings.BEDROCK_MODEL_ID:
            raise RuntimeError("BEDROCK_MODEL_ID não configurado")

    def get_llm(self):
        try:
            return ChatBedrockConverse(
                credentials_profile_name=self.settings.AWS_PROFILE,
                model_id=self.settings.BEDROCK_MODEL_ID,
                region_name=self.settings.AWS_REGION,
                temperature=self.settings.TEMPERATURE,
            )
        except Exception as e:
            logger.error("Falha ao inicializar o LLM do Bedrock", exc_info=True)
            raise Exception(f"Falha ao inicializar o LLM do Bedrock: {str(e)}")

    def create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente de IA prestativo e direto ao ponto."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

    async def generate_response_with_stream(
        self,
        prompt: str,
        session_id: str,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Faz stream do modelo, emitindo eventos:
          {"type":"token","text": "..."}
        No final, emite:
          {"type":"end","usage":{...},"history_size": N}
        """
        llm = self.get_llm()
        chain: Runnable = self.create_prompt() | llm
        chain_hist = self._with_history(chain, session_id)

        final_text_parts: list[str] = []

        async for chunk in chain_hist.astream(
            {"input": prompt},
            config={"configurable": {"session_id": session_id}},
        ):
            text_part = getattr(chunk, "content", None)
            print(f"chunk  -> -> {text_part}")

            if isinstance(text_part, str):
                final_text_parts.append(text_part)
                yield {"type": "token", "text": text_part}

            elif isinstance(text_part, list):
                for piece in text_part:
                    if isinstance(piece, str):
                        final_text_parts.append(piece)
                        yield {"type": "token", "text": piece}
                    elif isinstance(piece, dict) and "text" in piece:
                        final_text_parts.append(piece["text"])
                        yield {"type": "token", "text": piece["text"]}

        yield {
            "type": "end",
            "full_text": "".join(final_text_parts),
        }
