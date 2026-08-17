"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.errors import ApiException
from app.api.router import api_router
from app.api.schemas import ApiError, ApiErrorDetail, ErrorEnvelope
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

    @application.middleware("http")
    async def attach_request_id(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.request_id = request.headers.get("X-Request-ID", str(uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @application.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ApiErrorDetail(
                field=".".join(str(location) for location in item["loc"] if location != "body")
                or None,
                message=item["msg"],
                code=item["type"].upper(),
            )
            for item in error.errors()
        ]
        envelope = ErrorEnvelope(
            error=ApiError(
                code="VALIDATION_ERROR",
                message="The request contains invalid or incomplete data.",
                details=details,
                request_id=request.state.request_id,
            )
        )
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(envelope.model_dump(by_alias=True)),
        )

    @application.exception_handler(ApiException)
    async def handle_api_error(request: Request, error: ApiException) -> JSONResponse:
        envelope = ErrorEnvelope(
            error=ApiError(
                code=error.code,
                message=error.message,
                details=[],
                request_id=request.state.request_id,
            )
        )
        return JSONResponse(
            status_code=error.status_code,
            content=jsonable_encoder(envelope.model_dump(by_alias=True)),
        )

    @application.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request,
        error: StarletteHTTPException,
    ) -> JSONResponse:
        envelope = ErrorEnvelope(
            error=ApiError(
                code="HTTP_ERROR",
                message=str(error.detail),
                details=[],
                request_id=request.state.request_id,
            )
        )
        return JSONResponse(
            status_code=error.status_code,
            content=jsonable_encoder(envelope.model_dump(by_alias=True)),
            headers=error.headers,
        )

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
