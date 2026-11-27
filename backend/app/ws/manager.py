"""Registry of live WebSocket connections per user."""

import asyncio
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState

logger = logging.getLogger("app.ws")


class Connection:
    """One authenticated socket. Sends are serialized so the heartbeat task
    and event handlers never interleave frames."""

    def __init__(self, websocket: WebSocket, user_id: int):
        self.websocket = websocket
        self.user_id = user_id
        self._send_lock = asyncio.Lock()

    async def send(self, event_type: str, data: dict[str, Any] | None = None, *, reply_to: str | None = None) -> None:
        message: dict[str, Any] = {"type": event_type, "data": data or {}}
        if reply_to is not None:
            message["id"] = reply_to
        async with self._send_lock:
            if self.websocket.application_state == WebSocketState.CONNECTED:
                await self.websocket.send_json(message)

    async def send_error(self, code: str, message: str, *, reply_to: str | None = None) -> None:
        await self.send("error", {"code": code, "message": message}, reply_to=reply_to)

    async def close(self, code: int, reason: str = "") -> None:
        async with self._send_lock:
            if self.websocket.application_state == WebSocketState.CONNECTED:
                await self.websocket.close(code=code, reason=reason)


class ConnectionManager:
    """Tracks connections of this process. A user may have several (tabs, devices).

    Single-process for now (uvicorn runs one worker). Fan-out across workers
    needs Redis pub/sub on top of `send_to_user`; see docs/WS_PROTOCOL.md.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[Connection]] = defaultdict(set)

    def add(self, connection: Connection) -> None:
        self._connections[connection.user_id].add(connection)

    def remove(self, connection: Connection) -> None:
        user_connections = self._connections.get(connection.user_id)
        if user_connections is None:
            return
        user_connections.discard(connection)
        if not user_connections:
            del self._connections[connection.user_id]

    def is_online(self, user_id: int) -> bool:
        return user_id in self._connections

    def online_user_ids(self) -> set[int]:
        return set(self._connections)

    async def send_to_user(self, user_id: int, event_type: str, data: dict[str, Any] | None = None) -> int:
        """Send an event to every connection of the user. Returns how many got it."""
        delivered = 0
        for connection in list(self._connections.get(user_id, ())):
            try:
                await connection.send(event_type, data)
                delivered += 1
            except Exception:  # a dead socket must not break delivery to the others
                logger.warning("Dropping broken connection of user %s", user_id, exc_info=True)
                self.remove(connection)
        return delivered


manager = ConnectionManager()
