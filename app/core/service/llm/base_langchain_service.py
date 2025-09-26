import logging
from abc import ABC, abstractmethod
from typing import Callable, AsyncIterator

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.core.exceptions import NotFoundError, SessionError

logger = logging.getLogger(__name__)


class BaseLangChainService(ABC):
    store: dict[str, BaseChatMessageHistory] = {}

    @abstractmethod
    def get_llm(self):
        ...

    @abstractmethod
    def create_prompt(self, *args, **kwargs) -> ChatPromptTemplate:
        ...

    @abstractmethod
    async def generate_response_with_stream(self, *args, **kwargs) -> AsyncIterator[dict]:
        ...

    def end_session(self, session_id: str) -> None:
        try:
            if session_id not in self.store:
                logger.debug("Sessão não encontrada no store", extra={"session_id": session_id})
                raise NotFoundError(f"Sessão com ID '{session_id}' não encontrada")

            history = self._get_session_history(session_id)
            history.clear()
            del self.store[session_id]
            logger.debug("Sessão removida com sucesso", extra={"session_id": session_id})

        except Exception as e:
            logger.error("Falha ao limpar sessão", exc_info=True, extra={"session_id": session_id})
            raise SessionError(f"Erro ao encerrar sessão: {str(e)}")

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def _with_history(self, runnable: Runnable, session_id: str) -> RunnableWithMessageHistory:
        get_history_func: Callable[[None], BaseChatMessageHistory] = lambda _: self._get_session_history(session_id)
        with_message_history = RunnableWithMessageHistory(
            runnable,
            get_history_func,
            input_messages_key="input",
            history_messages_key="history",
        )
        return with_message_history
