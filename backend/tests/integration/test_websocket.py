import pytest
from starlette.websockets import WebSocketDisconnect

from app.core.config import get_settings
from app.core.security import create_token
from app.ws.events import registry
from app.ws.manager import manager


def access_token(client, username="alice"):
    client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": "s3cret-pass"},
    )
    r = client.post("/api/v1/auth/login", json={"email": f"{username}@example.com", "password": "s3cret-pass"})
    return r.json()["access_token"]


def expect_close(session, code):
    with pytest.raises(WebSocketDisconnect) as exc:
        while True:
            session.receive_json()
    assert exc.value.code == code


@pytest.fixture
def fast_ws(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ws_auth_timeout_seconds", 0.2)
    monkeypatch.setattr(settings, "ws_heartbeat_interval_seconds", 0.05)
    monkeypatch.setattr(settings, "ws_heartbeat_timeout_seconds", 0.2)


def test_auth_ok(client):
    token = access_token(client)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "data": {"token": token}})
        msg = ws.receive_json()

    assert msg["type"] == "auth.ok"
    assert isinstance(msg["data"]["user_id"], int)


@pytest.mark.parametrize(
    "first_message",
    [
        {"type": "auth", "data": {"token": "garbage"}},
        {"type": "auth", "data": {}},
        {"type": "chat.message", "data": {"text": "hi"}},
        "not json",
    ],
)
def test_unauthorized_sockets_are_rejected(client, first_message):
    with client.websocket_connect("/ws") as ws:
        if isinstance(first_message, str):
            ws.send_text(first_message)
        else:
            ws.send_json(first_message)
        expect_close(ws, 4401)


def test_refresh_token_is_not_accepted(client):
    access_token(client)
    refresh = client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "s3cret-pass"}
    ).json()["refresh_token"]

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "data": {"token": refresh}})
        expect_close(ws, 4401)


def test_token_of_unknown_user_is_rejected(client):
    token, _ = create_token("999", "access")
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "data": {"token": token}})
        expect_close(ws, 4401)


def test_auth_timeout(client, fast_ws):
    with client.websocket_connect("/ws") as ws:
        expect_close(ws, 4401)


def test_ping_pong_and_protocol_errors(client):
    token = access_token(client)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "data": {"token": token}})
        ws.receive_json()

        ws.send_json({"type": "ping", "id": "1"})
        assert ws.receive_json() == {"type": "pong", "data": {}, "id": "1"}

        ws.send_text("{oops")
        assert ws.receive_json()["data"]["code"] == "invalid_message"

        ws.send_bytes(b"\x00")
        assert ws.receive_json()["data"]["code"] == "invalid_message"

        ws.send_json({"type": "nope", "id": "2"})
        error = ws.receive_json()
        assert error["type"] == "error"
        assert error["data"]["code"] == "unknown_event"
        assert error["id"] == "2"

        ws.send_json({"type": "auth", "data": {"token": token}})
        assert ws.receive_json()["data"]["code"] == "already_authenticated"

        # Errors do not close the connection.
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


def test_heartbeat_pings_then_closes_silent_client(client, fast_ws):
    token = access_token(client)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "data": {"token": token}})
        assert ws.receive_json()["type"] == "auth.ok"
        assert ws.receive_json()["type"] == "ping"
        expect_close(ws, 4408)


@pytest.fixture
def notify_handler():
    async def handler(conn, data, message_id):
        delivered = await manager.send_to_user(conn.user_id, "test.notified", {"text": data["text"]})
        await conn.send("test.done", {"delivered": delivered}, reply_to=message_id)

    registry.add("test.notify", handler)
    yield
    registry.remove("test.notify")


def test_send_to_user_reaches_every_connection(client, notify_handler):
    token = access_token(client)
    with client.websocket_connect("/ws") as tab1, client.websocket_connect("/ws") as tab2:
        for tab in (tab1, tab2):
            tab.send_json({"type": "auth", "data": {"token": token}})
            user_id = tab.receive_json()["data"]["user_id"]
        assert manager.is_online(user_id)

        tab1.send_json({"type": "test.notify", "data": {"text": "hello"}, "id": "n1"})
        assert tab1.receive_json() == {"type": "test.notified", "data": {"text": "hello"}}
        assert tab1.receive_json() == {"type": "test.done", "data": {"delivered": 2}, "id": "n1"}
        assert tab2.receive_json() == {"type": "test.notified", "data": {"text": "hello"}}

    assert not manager.is_online(user_id)


def test_handler_errors_are_reported(client):
    async def broken(conn, data, message_id):
        raise RuntimeError("boom")

    registry.add("test.broken", broken)
    try:
        token = access_token(client)
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "auth", "data": {"token": token}})
            ws.receive_json()
            ws.send_json({"type": "test.broken"})
            assert ws.receive_json()["data"]["code"] == "internal_error"
    finally:
        registry.remove("test.broken")


def test_reserved_event_types_cannot_be_registered():
    async def handler(conn, data, message_id):
        pass

    for reserved in ("auth", "ping", "pong"):
        with pytest.raises(ValueError):
            registry.add(reserved, handler)
