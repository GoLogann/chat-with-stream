from dependency_injector import containers, providers

from app.core.config import Settings
from app.core.service.chat.chat_service import ChatService
from app.core.service.llm.bedrock_service import BedrockChatService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.adapter.routers.websocket_router",
        ]
    )

    config = providers.Singleton(Settings)

    bedrock_service = providers.Factory(
        BedrockChatService,
        settings=config
    )

    chat_service = providers.Singleton(
        ChatService,
        llm_service=bedrock_service
    )
