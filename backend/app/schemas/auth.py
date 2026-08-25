"""Схемы авторизации."""

from pydantic import BaseModel, Field

from app.schemas.common import EmailAddress


class LoginRequest(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
    all_sessions: bool = False
