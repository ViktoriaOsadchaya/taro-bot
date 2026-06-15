"""Сборка всех API-роутеров."""

from fastapi import APIRouter

from app.api.routers import cards, health, index, reading_sessions, readings, spreads, users

API_V1_PREFIX = "/api/v1"

router = APIRouter()
router.include_router(index.router)
router.include_router(health.router)
router.include_router(spreads.router, prefix=API_V1_PREFIX)
router.include_router(cards.router, prefix=API_V1_PREFIX)
router.include_router(users.router, prefix=API_V1_PREFIX)
router.include_router(reading_sessions.router, prefix=API_V1_PREFIX)
router.include_router(readings.router, prefix=API_V1_PREFIX)
