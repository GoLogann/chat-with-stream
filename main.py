import logging
from fastapi import FastAPI
from app.container import Container
from app.adapter.routers import websocket_router
from app.core.config import Settings

logging.basicConfig(level=logging.INFO)

def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(title="Chat With Stream WS - By Logan")
    app.container = container
    app.include_router(websocket_router.router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = Settings()
    port = int(getattr(settings, "PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
