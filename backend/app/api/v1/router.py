"""Агрегирующий роутер API v1."""

from fastapi import APIRouter

from app.api.v1 import auth, dictionaries, documents, notifications, requests, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(requests.router)
api_router.include_router(documents.router)
api_router.include_router(notifications.router)
api_router.include_router(dictionaries.router)
