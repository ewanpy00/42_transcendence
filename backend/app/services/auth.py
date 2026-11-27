"""Registration, login, token refresh and logout."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import count
from typing import Protocol

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.security import (
    InvalidTokenError,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import TokenPair


class AuthError(Exception):
    """Wrong credentials or an unusable token. Maps to 401."""


class UserAlreadyExistsError(Exception):
    """Email or username is taken. Maps to 409."""

    def __init__(self, field_name: str):
        super().__init__(f"{field_name} is already registered")
        self.field_name = field_name


@dataclass
class UserRecord:
    id: int
    email: str
    username: str
    hashed_password: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class UserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> UserRecord | None: ...
    async def get_by_email(self, email: str) -> UserRecord | None: ...
    async def get_by_username(self, username: str) -> UserRecord | None: ...
    async def create(self, email: str, username: str, hashed_password: str) -> UserRecord: ...


class InMemoryUserRepository:
    """Temporary store until the SQLAlchemy `User` model lands (DB-02, #10).

    Data is lost on restart. Replace `get_user_repository` in `core/deps.py`
    with a database-backed implementation of `UserRepository`.
    """

    def __init__(self) -> None:
        self._users: dict[int, UserRecord] = {}
        self._ids = count(1)

    async def get_by_id(self, user_id: int) -> UserRecord | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> UserRecord | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def get_by_username(self, username: str) -> UserRecord | None:
        wanted = username.lower()
        return next((u for u in self._users.values() if u.username.lower() == wanted), None)

    async def create(self, email: str, username: str, hashed_password: str) -> UserRecord:
        user = UserRecord(
            id=next(self._ids),
            email=email,
            username=username,
            hashed_password=hashed_password,
        )
        self._users[user.id] = user
        return user


class RefreshTokenStore:
    """Allow-list of live refresh tokens in Redis, keyed by `jti`.

    A refresh token is valid only while its key exists. Refreshing deletes the
    key (rotation), logout deletes it too, and Redis expires it with the token.
    """

    PREFIX = "auth:refresh:"

    def __init__(self, redis: Redis):
        self._redis = redis

    async def add(self, jti: str, user_id: str, expires_at: datetime) -> None:
        ttl = max(1, int((expires_at - datetime.now(UTC)).total_seconds()))
        await self._redis.set(self.PREFIX + jti, user_id, ex=ttl)

    async def pop(self, jti: str) -> str | None:
        value = await self._redis.getdel(self.PREFIX + jti)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    async def remove(self, jti: str) -> None:
        await self._redis.delete(self.PREFIX + jti)


class AuthService:
    def __init__(self, users: UserRepository, refresh_tokens: RefreshTokenStore):
        self._users = users
        self._refresh_tokens = refresh_tokens

    async def register(self, email: str, username: str, password: str) -> UserRecord:
        if await self._users.get_by_email(email):
            raise UserAlreadyExistsError("email")
        if await self._users.get_by_username(username):
            raise UserAlreadyExistsError("username")
        return await self._users.create(email, username, hash_password(password))

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self._users.get_by_email(email)
        if not verify_password(password, user.hashed_password if user else None):
            raise AuthError("Invalid email or password")
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = self._decode_refresh(refresh_token)
        owner = await self._refresh_tokens.pop(payload.jti)
        if owner is None or owner != payload.sub:
            raise AuthError("Refresh token is revoked or already used")
        user = await self._users.get_by_id(int(payload.sub))
        if user is None:
            raise AuthError("User no longer exists")
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        payload = self._decode_refresh(refresh_token)
        await self._refresh_tokens.remove(payload.jti)

    async def _issue_tokens(self, user: UserRecord) -> TokenPair:
        access_token, _ = create_token(str(user.id), "access")
        refresh_token, refresh = create_token(str(user.id), "refresh")
        await self._refresh_tokens.add(refresh.jti, refresh.sub, refresh.exp)
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=get_settings().access_token_expire_minutes * 60,
        )

    @staticmethod
    def _decode_refresh(token: str):
        try:
            return decode_token(token, "refresh")
        except InvalidTokenError as exc:
            raise AuthError("Invalid refresh token") from exc
