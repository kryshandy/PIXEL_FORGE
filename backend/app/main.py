"""FastAPI application factory and ASGI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=(
            "API du copilote IA Pixel Forge pour la complétion et la production "
            "de puits pétroliers conventionnels."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix="/api/v1")

    @application.get("/", tags=["system"], summary="Informations de l'API")
    def api_information() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": settings.version,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return application


app = create_app()
