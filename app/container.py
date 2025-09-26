from dependency_injector import containers, providers
from app.core.config import Settings
from app.core.service.chat.chat_service import ChatService
from app.core.service.llm.bedrock_service import BedrockChatService
from app.domain.repositories.chat_repository import ChatRepository
from app.infra.dynamodb import DynamoClient

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.adapter.routers.websocket_router",
            "app.adapter.routers.chat_rest_router",
            "app.adapter.routers.frontend_router",
        ]
    )

    config = providers.Singleton(Settings)
    
    ddb_client = providers.Singleton(
        DynamoClient, 
        settings=config
    )

    chat_repository = providers.Singleton(
        ChatRepository, 
        dynamo=ddb_client
    )
    
    bedrock_service = providers.Factory(
        BedrockChatService,
        settings=config,
        repo=chat_repository,   
    )

    chat_service = providers.Singleton(
        ChatService,
        llm_service=bedrock_service,
        repo=chat_repository,  
    )