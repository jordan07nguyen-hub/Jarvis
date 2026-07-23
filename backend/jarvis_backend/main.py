from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jarvis_backend.api.routes import chat, health, websocket
from jarvis_backend.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    # No browser page is a legitimate caller of this API (the macOS app talks
    # to it natively, not via a page's JS), so cross-origin browser access is
    # denied unless the user explicitly lists origins to allow.
    if settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(websocket.router)

    return app


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run("jarvis_backend.main:app", host=settings.host, port=settings.port, reload=True)


if __name__ == "__main__":
    run()
