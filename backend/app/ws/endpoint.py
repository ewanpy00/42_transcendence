"""The `/ws` endpoint: auth handshake, heartbeat and event dispatch.

Protocol: docs/WS_PROTOCOL.md.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from time import monotonic
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from starlette.websockets import WebSocketState

from app.core.config import get_settings
from app.core.deps import get_user_repository
from app.core.security import InvalidTokenError, decode_token
from app.services.auth import UserRecord, UserRepository
from app.ws.events import Envelope, registry
from app.ws.manager import Connection, manager

logger = logging.getLogger("app.ws")

router = APIRouter()

CLOSE_UNAUTHORIZED = 4401
CLOSE_HEARTBEAT_TIMEOUT = 4408


@dataclass
class _Activity:
    last_seen: float = field(default_factory=monotonic)


async def _receive_text(websocket: WebSocket) -> str | None:
    """Next text frame; None for a binary frame. Raises WebSocketDisconnect."""
    message = await websocket.receive()
    if message["type"] == "websocket.disconnect":
        raise WebSocketDisconnect(message.get("code", 1000), message.get("reason"))
    return message.get("text")


async def _authenticate(websocket: WebSocket, users: UserRepository, timeout: float) -> UserRecord | None:
    async def reject(reason: str) -> None:
        await websocket.close(code=CLOSE_UNAUTHORIZED, reason=reason)

    try:
        raw = await asyncio.wait_for(_receive_text(websocket), timeout)
    except TimeoutError:
        await reject("Authentication timeout")
        return None

    try:
        envelope = Envelope.model_validate_json(raw or "")
    except ValidationError:
        envelope = None
    token = envelope.data.get("token") if envelope and envelope.type == "auth" else None
    if not isinstance(token, str):
        await reject("Expected an auth message")
        return None

    try:
        payload = decode_token(token, "access")
    except InvalidTokenError:
        await reject("Invalid or expired token")
        return None

    user = await users.get_by_id(int(payload.sub))
    if user is None:
        await reject("User no longer exists")
    return user


async def _heartbeat(conn: Connection, activity: _Activity, interval: float, timeout: float) -> None:
    try:
        while True:
            await asyncio.sleep(interval)
            if monotonic() - activity.last_seen > timeout:
                await conn.close(CLOSE_HEARTBEAT_TIMEOUT, "Heartbeat timeout")
                return
            await conn.send("ping")
    except asyncio.CancelledError:
        raise
    except Exception:  # socket already gone; the receive loop cleans up
        logger.debug("Heartbeat stopped for user %s", conn.user_id, exc_info=True)


async def _dispatch(conn: Connection, raw: str | None) -> None:
    if raw is None:
        await conn.send_error("invalid_message", "Only JSON text frames are supported")
        return
    try:
        envelope = Envelope.model_validate_json(raw)
    except ValidationError:
        await conn.send_error("invalid_message", "Expected JSON object {type, data?, id?}")
        return

    if envelope.type == "pong":
        return
    if envelope.type == "ping":
        await conn.send("pong", reply_to=envelope.id)
        return
    if envelope.type == "auth":
        await conn.send_error("already_authenticated", "Connection is already authenticated", reply_to=envelope.id)
        return

    handler = registry.get(envelope.type)
    if handler is None:
        await conn.send_error("unknown_event", f"Unknown event type '{envelope.type}'", reply_to=envelope.id)
        return

    try:
        await handler(conn, envelope.data, envelope.id)
    except ValidationError as exc:
        await conn.send_error("invalid_data", str(exc), reply_to=envelope.id)
    except Exception:
        logger.exception("Handler for '%s' failed", envelope.type)
        await conn.send_error("internal_error", "Internal server error", reply_to=envelope.id)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    users: Annotated[UserRepository, Depends(get_user_repository)],
):
    settings = get_settings()
    await websocket.accept()

    try:
        user = await _authenticate(websocket, users, settings.ws_auth_timeout_seconds)
    except WebSocketDisconnect:
        return
    if user is None:
        return

    conn = Connection(websocket, user.id)
    activity = _Activity()
    manager.add(conn)
    heartbeat = asyncio.create_task(
        _heartbeat(
            conn,
            activity,
            settings.ws_heartbeat_interval_seconds,
            settings.ws_heartbeat_timeout_seconds,
        )
    )
    try:
        await conn.send("auth.ok", {"user_id": user.id})
        while websocket.application_state == WebSocketState.CONNECTED:
            raw = await _receive_text(websocket)
            activity.last_seen = monotonic()
            await _dispatch(conn, raw)
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat.cancel()
        manager.remove(conn)
