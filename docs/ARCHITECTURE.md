# Architecture

```
Browser --HTTPS--> nginx --/-------> frontend (React, static)
                         |--/api---> backend (FastAPI) --> PostgreSQL
                         |--/ws----> backend (WebSocket)
                         `--/uploads (files)
CLI --API key--> /public/v1 (rate limited)
```

## Backend layers

`api/v1` (thin routers) -> `services` (business logic) -> `models` (SQLAlchemy). `schemas` are Pydantic models. `ws/` holds the connection manager and event handlers. The matchmaking queue lives in Redis (already in docker-compose), which also lets WebSocket events scale across workers; durable session state is persisted in PostgreSQL.

## Chat session states

`WAITING` -> `CONNECTED` -> `DISCONNECTED` (leave / skip / connection lost beyond grace period). After skip the user re-enters the queue.

## Module -> issues map

| Module | Issues |
|---|---|
| Frontend framework (React) | FE1-01, FE2-01 |
| Backend framework (FastAPI) | BE-01 |
| WebSockets / real-time | BE-05..08, FE2-02..04 |
| User interaction (chat, profile, friends) | BE-04, BE-08, DB-04, FE1-04/06, FE2-04 |
| Public API + key + rate limit + docs | BE-10..12, OPS-07 |
| ORM (SQLAlchemy) | DB-02 |
| Notifications | DB-05, FE1-07 |
| Advanced search | DB-06, FE2-06 |
| File upload | BE-09, FE2-05 |
| Browser support | OPS-08, FE2-08 |
| User management + auth | BE-02, BE-04, FE1-02/04 |
| OAuth 2.0 | BE-03, FE1-03 |
| Analytics dashboard | DB-07, FE1-08 |
| Health/status + backups | OPS-05, OPS-06 |
| (optional) Auto-translation | BE-13, FE2-07 |

> **Double-check the point count.** In the official 42 subject, the Major "framework for both frontend and backend" normally *replaces* the two separate Minors (frontend framework / backend framework) rather than adding to them. If that applies, remove the two Minors: 18 points total, 4 bonus. Verify against the current subject before evaluation.
