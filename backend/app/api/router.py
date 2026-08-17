"""Versioned API router."""

from fastapi import APIRouter

from app.api.routes.engineering_calculations import router as engineering_calculations_router
from app.api.routes.health import router as health_router
from app.api.routes.recommendations import router as recommendations_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(engineering_calculations_router)
api_router.include_router(recommendations_router)
