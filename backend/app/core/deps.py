"""Shared FastAPI dependencies."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.security import InvalidTokenError, decode_token
from app.services.auth import (
    AuthService,
    InMemoryUserRepository,
    RefreshTokenStore,
    UserRecord,
    UserRepository,
)

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


@lru_cache
def get_user_repository() -> UserRepository:
    # TODO(DB-02, #10): return the SQLAlchemy-backed repository.
    return InMemoryUserRepository()


def get_auth_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AuthService:
    return AuthService(users, RefreshTokenStore(redis))


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserRecord:
    if credentials is None:
        raise _unauthorized("Not authenticated")
    try:
        payload = decode_token(credentials.credentials, "access")
    except InvalidTokenError:
        raise _unauthorized("Invalid or expired access token") from None
    user = await users.get_by_id(int(payload.sub))
    if user is None:
        raise _unauthorized("User no longer exists")
    return user


CurrentUser = Annotated[UserRecord, Depends(get_current_user)]
