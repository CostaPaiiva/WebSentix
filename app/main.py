from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import api, exports, pages
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="WebSentix",
        description="Aplicação web de análise de sentimentos com FastAPI",
        version="1.0.0",
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(pages.router)
    app.include_router(api.router, prefix="/api", tags=["analysis"])
    app.include_router(exports.router, prefix="/exports", tags=["exports"])

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
