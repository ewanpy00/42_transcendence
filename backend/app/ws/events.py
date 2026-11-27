"""Event envelope and handler registry.

Feature modules register their client events here, for example in `ws/chat.py`:

    from app.ws.events import registry

    @registry.on("chat.message")
    async def send_message(conn, data, message_id): ...
"""

from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, Field

from app.ws.manager import Connection

Handler = Callable[[Connection, dict[str, Any], str | None], Awaitable[None]]

# Handled by the endpoint itself; feature modules cannot take these names.
RESERVED_TYPES = frozenset({"auth", "ping", "pong"})


class Envelope(BaseModel):
    type: str = Field(min_length=1, max_length=64)
    data: dict[str, Any] = Field(default_factory=dict)
    id: str | None = Field(default=None, max_length=64)


class EventRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def on(self, event_type: str) -> Callable[[Handler], Handler]:
        def decorator(handler: Handler) -> Handler:
            self.add(event_type, handler)
            return handler

        return decorator

    def add(self, event_type: str, handler: Handler) -> None:
        if event_type in RESERVED_TYPES:
            raise ValueError(f"'{event_type}' is reserved by the protocol")
        if event_type in self._handlers:
            raise ValueError(f"handler for '{event_type}' is already registered")
        self._handlers[event_type] = handler

    def remove(self, event_type: str) -> None:
        self._handlers.pop(event_type, None)

    def get(self, event_type: str) -> Handler | None:
        return self._handlers.get(event_type)


registry = EventRegistry()
