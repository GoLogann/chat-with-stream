import logging
from abc import ABC, abstractmethod
from typing import Callable, AsyncIterator

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.domain.repositories.chat_repository import ChatRepository

logger = logging.getLogger(__name__)


class BaseLangChainService(ABC):
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    @abstractmethod
    def get_llm(self):
        ...

    @abstractmethod
    def create_prompt(self, *args, **kwargs) -> ChatPromptTemplate:
        ...

    @abstractmethod
    async def generate_response_with_stream(self, *args, **kwargs) -> AsyncIterator[dict]:
        ...

    def _get_session_history(self, chat_id: str) -> ChatMessageHistory:
        """Carrega histórico de mensagens do Dynamo e devolve ChatMessageHistory"""
        hist = ChatMessageHistory()
        messages = self.repo.get_messages(chat_id=chat_id, limit=1000)["items"]
        for m in messages:
            hist.add_message({"role": m["role"], "content": m["content"]})
        return hist

    def _with_history(self, runnable: Runnable, chat_id: str) -> RunnableWithMessageHistory:
        get_history_func: Callable[[None], ChatMessageHistory] = lambda _: self._get_session_history(chat_id)
        return RunnableWithMessageHistory(
            runnable,
            get_history_func,
            input_messages_key="input",
            history_messages_key="history",
        )
