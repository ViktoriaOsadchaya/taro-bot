"""Сборка всех API-роутеров."""

from fastapi import APIRouter

from app.api.routers import cards, health, index, reading_sessions, readings, spreads, users

router = APIRouter()
router.include_router(index.router)
router.include_router(health.router)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(spreads.router)
api_router.include_router(cards.router)
api_router.include_router(users.router)
api_router.include_router(reading_sessions.router)
api_router.include_router(readings.router)

router.include_router(api_router)
