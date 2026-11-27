# WebSocket protocol

One socket per browser tab carries all real-time traffic (matchmaking, chat, notifications).

- **URL:** `wss://<host>/ws` (nginx proxies `/ws` to the backend; local backend: `ws://localhost:8000/ws`).
- **Frames:** UTF-8 text frames with one JSON object each. Binary frames are answered with an `invalid_message` error.

## Message envelope

Both directions use the same shape:

```json
{ "type": "chat.message", "data": { "text": "hi" }, "id": "c-17" }
```

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | string, 1-64 chars | yes | Event name, `<area>.<action>` (e.g. `matchmaking.join`). |
| `data` | object | no, defaults to `{}` | Event payload. |
| `id` | string, up to 64 chars | no | Set by the client to match a reply. The server copies it into its direct reply (`pong`, `error`, or the feature's response) and omits it on pushed events. |

## Connection lifecycle

```
client                                server
  |-- open wss://host/ws ------------->|
  |-- {"type":"auth","data":{"token":<access JWT>}} -->|   within 5 s
  |<-- {"type":"auth.ok","data":{"user_id":1}} -------|
  |                                    |
  |<-- {"type":"ping"} ---------------|   every 25 s
  |-- {"type":"pong"} --------------->|
  |        ... feature events ...      |
```

1. **Authenticate first.** The first frame must be `auth` with a valid **access** token from `POST /api/v1/auth/login` (or `/refresh`). Browsers cannot set headers on a WebSocket, and a token in the URL would end up in proxy logs, so the token goes in this first message.
2. Anything else, an invalid or expired token, a refresh token, or nothing within **5 s** closes the socket with code **4401**.
3. After `auth.ok` the connection stays authenticated until it closes, even if the access token expires meanwhile. To act as another user, open a new socket.

## Heartbeat

- The server sends `{"type":"ping"}` every **25 s**. The client should answer `{"type":"pong"}`.
- Any client frame counts as activity. If the server hears nothing for **60 s**, it closes with **4408**.
- The client may send `{"type":"ping","id":"..."}` at any time; the server answers `{"type":"pong","id":"..."}`. Useful to measure latency or detect a dead link from the client side.

Protocol-level WebSocket ping/pong frames from the browser or proxies do not count: browsers do not expose them, so the heartbeat is in JSON.

## Close codes

| Code | Meaning | Client should |
|---|---|---|
| 1000 | Normal close | nothing |
| 4401 | Not authenticated (no/invalid/expired token, auth timeout, user deleted) | refresh the access token, then reconnect; if refresh fails, go to login |
| 4408 | Heartbeat timeout | reconnect with backoff |
| 1006 / other | Network drop, server restart | reconnect with exponential backoff (e.g. 1 s, 2 s, 4 s ... max 30 s) |

## Built-in events

Client → server:

| `type` | `data` | Notes |
|---|---|---|
| `auth` | `{ "token": string }` | First frame only. Sending it again returns `already_authenticated`. |
| `ping` | `{}` | Server replies `pong`. |
| `pong` | `{}` | Reply to the server's `ping`. |

Server → client:

| `type` | `data` | Notes |
|---|---|---|
| `auth.ok` | `{ "user_id": number }` | Handshake succeeded. |
| `ping` | `{}` | Heartbeat. |
| `pong` | `{}` | Reply to the client's `ping`, carries its `id`. |
| `error` | `{ "code": string, "message": string }` | The connection stays open. Carries the request `id` when there was one. |

### Error codes

| `code` | When |
|---|---|
| `invalid_message` | Not JSON, not an object, missing `type`, or a binary frame. |
| `unknown_event` | No handler for this `type`. |
| `invalid_data` | The handler rejected `data` (validation failed). |
| `already_authenticated` | A second `auth` on the same socket. |
| `internal_error` | The handler crashed; details are in the server log. |

Feature handlers may add their own codes (e.g. `queue_full`); they are listed in the feature's section below.

## Feature events

Each feature adds its section here in its own PR, so the backend and frontend agree on names and payloads before implementation.

- Matchmaking (BE-06 / FE2-03): `matchmaking.*`
- Chat sessions and messages (BE-07, BE-08 / FE2-04): `chat.*`
- Notifications (DB-05 / FE1-07): `notification.*`

## Backend notes

- Handlers register in `app/ws/events.py`: `@registry.on("chat.message") async def handler(conn, data, message_id)`. `auth`, `ping` and `pong` are reserved.
- `app.ws.manager.manager.send_to_user(user_id, type, data)` pushes an event to every open tab of a user.
- Connections are tracked per process. Uvicorn runs one worker today; running several needs fan-out over Redis pub/sub inside `send_to_user`.
- Timings are configurable: `WS_AUTH_TIMEOUT_SECONDS`, `WS_HEARTBEAT_INTERVAL_SECONDS`, `WS_HEARTBEAT_TIMEOUT_SECONDS`.
