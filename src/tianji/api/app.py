"""FastAPI application factory for Tianji."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tianji.config import get_config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = get_config()

    app = FastAPI(
        title="天机 API — Tianji",
        description="Chinese Metaphysics API: BaZi (八字), Liu Yao (六爻), Zi Wei Dou Shu (紫微斗数)",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from tianji.api.routes import router
    app.include_router(router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "tianji", "version": "0.1.0"}

    return app
