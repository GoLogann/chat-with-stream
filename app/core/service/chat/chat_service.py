from __future__ import annotations
from typing import AsyncIterator, Dict, Any

from app.core.service.llm.bedrock_service import BedrockChatService
from app.domain.repositories.chat_repository import ChatRepository


class ChatService:
    def __init__(self, llm_service: BedrockChatService, repo: ChatRepository):
        self.llm_service = llm_service
        self.repo = repo

    async def ask_stream(
        self,
        *,
        user_id: str,
        question: str,
        chat_id: str | None = None,
        session_id: str | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Orquestra todo o fluxo:
        - cria chat/session se não existirem
        - persiste pergunta
        - stream da resposta
        - persiste resposta
        """

        if not chat_id:
            title = (question[:50] + '...') if len(question) > 50 else question
            chat = self.repo.create_chat(user_id=user_id, title=title)
            chat_id = chat["chat_id"]

        if not session_id:
            sess = self.repo.start_session(user_id=user_id, chat_id=chat_id)
            session_id = sess["session_id"]

        self.repo.append_message(chat_id=chat_id, user_id=user_id, role="user", content=question)
        self.repo.update_chat_preview_and_ts(user_id=user_id, chat_id=chat_id, preview=question[:160])
        self.repo.touch_session(user_id=user_id, session_id=session_id)

        yield {"type": "start", "session_id": session_id, "chat_id": chat_id}

        full_text = []
        async for event in self.llm_service.generate_response_with_stream(
            prompt=question, chat_id=chat_id, session_id=session_id
        ):
            if event.get("type") == "token":
                full_text.append(event.get("text", ""))
                yield event
            elif event.get("type") == "error":
                yield event

        final = "".join(full_text)

        self.repo.append_message(chat_id=chat_id, user_id=user_id, role="assistant", content=final)
        self.repo.update_chat_preview_and_ts(user_id=user_id, chat_id=chat_id, preview=final[:160])

        yield {"type": "end", "session_id": session_id, "chat_id": chat_id, "full_text": final}

    def end_session(self, user_id: str, session_id: str) -> None:
        self.repo.end_session(user_id, session_id)

    def list_chats(self, user_id: str, limit: int = 20, cursor: dict | None = None):
        return self.repo.list_chats(user_id, limit, cursor)

    def history(self, chat_id: str, limit: int = 100, cursor: dict | None = None):
        return self.repo.get_messages(chat_id, limit, cursor)

    def update_chat_title(self, user_id: str, chat_id: str, new_title: str):
        self.repo.update_chat_title(user_id=user_id, chat_id=chat_id, new_title=new_title)