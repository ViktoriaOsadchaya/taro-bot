"""Сборка API v1 роутеров (без index и health)."""

from fastapi import APIRouter

from app.api.deps.auth_deps import CURRENT_USER
from app.api.routers import auth, cards, reading_sessions, readings, spreads, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

protected_router = APIRouter(dependencies=[CURRENT_USER])
protected_router.include_router(spreads.router, prefix="/spreads", tags=["spreads"])
protected_router.include_router(cards.router, prefix="/cards", tags=["cards"])
protected_router.include_router(users.router, prefix="/users", tags=["users"])
protected_router.include_router(reading_sessions.router, prefix="/readings/sessions", tags=["reading-sessions"])
protected_router.include_router(readings.router, prefix="/readings", tags=["readings"])

api_router.include_router(protected_router)
