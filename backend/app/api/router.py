"""Сборка всех API-роутеров."""

from fastapi import APIRouter

from app.api.routers import cards, health, reading_sessions, readings, spreads, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(spreads.router)
api_router.include_router(cards.router)
api_router.include_router(users.router)
api_router.include_router(reading_sessions.router)
api_router.include_router(readings.router)

# Health вне /api/v1 — для docker/k8s probes.
health_router = health.router
