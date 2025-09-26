from __future__ import annotations

import logging
import asyncio
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
        timeout: int = 60,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream do modelo emitindo:
          {"type":"token","text": "..."}
          {"type":"end","usage":{...},"history_size": N,"full_text":"..."}
          {"type":"error","message":"..."}
        """

        llm = self.get_llm()
        chain: Runnable = self.create_prompt() | llm
        chain_hist = self._with_history(chain, session_id)

        gen = chain_hist.astream_events(
            {"input": prompt},
            config={"configurable": {"session_id": session_id}},
        )

        try:
            final_text = ""
            usage = {}

            while True:
                try:
                    event = await asyncio.wait_for(anext(gen), timeout=timeout)
                except StopAsyncIteration:
                    break

                ev_type = event.get("event")
                ev_name = event.get("name")

                if ev_type == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    text_part = getattr(chunk, "content", None)

                    if isinstance(text_part, str):
                        yield {"type": "token", "text": text_part}
                    elif isinstance(text_part, list):
                        for piece in text_part:
                            if isinstance(piece, str):
                                yield {"type": "token", "text": piece}
                            elif isinstance(piece, dict) and "text" in piece:
                                yield {"type": "token", "text": piece["text"]}

                elif ev_type == "on_chain_end" and ev_name == "RunnableWithMessageHistory":
                    output = event["data"].get("output")
                    if output:
                        # texto final
                        if hasattr(output, "content"):
                            if isinstance(output.content, str):
                                final_text = output.content
                            elif isinstance(output.content, list):
                                final_text = "".join(
                                    part["text"]
                                    for part in output.content
                                    if isinstance(part, dict) and part.get("type") == "text"
                                )

                        usage_meta = getattr(output, "usage_metadata", None)
                        if usage_meta:
                            usage = {
                                "input_tokens": usage_meta.get("input_tokens"),
                                "output_tokens": usage_meta.get("output_tokens"),
                                "total_tokens": usage_meta.get("total_tokens"),
                            }

        except asyncio.TimeoutError:
            yield {"type": "error", "message": f"Timeout de {timeout}s atingido"}
            return
        except Exception as e:
            logger.exception("Erro durante o streaming")
            yield {"type": "error", "message": str(e)}
            return

        history = self._get_session_history(session_id)
        history_size = len(getattr(history, "messages", []))

        yield {
            "type": "end",
            "usage": usage,
            "history_size": history_size,
            "full_text": final_text,
        }