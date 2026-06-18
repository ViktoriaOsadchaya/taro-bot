"""Сборка API v1 роутеров (без index и health)."""

from fastapi import APIRouter

from app.api.routers import cards, reading_sessions, readings, spreads, users

api_router = APIRouter()
api_router.include_router(spreads.router, prefix="/spreads", tags=["spreads"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reading_sessions.router, prefix="/readings/sessions", tags=["reading-sessions"])
api_router.include_router(readings.router, prefix="/readings", tags=["readings"])
