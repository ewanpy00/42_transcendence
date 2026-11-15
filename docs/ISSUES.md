# Issues by developer

_Generated from `scripts/issues_data.py`. Do not edit by hand._

Roles: **BE** backend, **DB** database + data-heavy API, **OPS** deploy/devops, **FE1**/**FE2** frontend.
One issue = one branch (`feature/<id>-<slug>` from `develop`) = one PR.
Dependencies mean: do not merge before the dependency (you can start earlier against mocks).

Phases: **P0** Foundation -> **P1** Core (auth, profile, WebSocket) -> **P2** Matchmaking & chat -> **P3** Social features & modules -> **P4** Polish

## OPS - Deploy / DevOps

| ID | Phase | Branch | Task | Depends on |
|---|---|---|---|---|
| OPS-01 | P0 | `feature/ops-01-docker-compose` | Docker Compose setup | - |
| OPS-02 | P0 | `feature/ops-02-env-secrets` | Environment & secrets management | - |
| OPS-03 | P0 | `feature/ops-03-ci` | CI pipeline (GitHub Actions) | - |
| OPS-04 | P1 | `feature/ops-04-nginx-https` | nginx reverse proxy with HTTPS | OPS-01 |
| OPS-05 | P3 | `feature/ops-05-healthcheck-status` | Health check & status page | BE-01 |
| OPS-06 | P3 | `feature/ops-06-backup-dr` | Automated backups & disaster recovery | DB-02 |
| OPS-07 | P3 | `feature/ops-07-cli` | CLI for the public API | BE-11 |
| OPS-08 | P4 | `feature/ops-08-browser-support` | Browser support matrix | - |

## DB - Database + data-heavy API

| ID | Phase | Branch | Task | Depends on |
|---|---|---|---|---|
| DB-01 | P0 | `feature/db-01-schema-design` | Database schema design & ERD | - |
| DB-02 | P0 | `feature/db-02-models-alembic` | SQLAlchemy models & Alembic | DB-01 |
| DB-03 | P1 | `feature/db-03-seed-data` | Seed data script | DB-02 |
| DB-04 | P2 | `feature/db-04-friends` | Friends system API | BE-02 |
| DB-05 | P3 | `feature/db-05-notifications` | Notification system | BE-05 |
| DB-06 | P3 | `feature/db-06-search` | Advanced search with filters, sorting, pagination | DB-02 |
| DB-07 | P3 | `feature/db-07-analytics` | User activity analytics | DB-02 |
| DB-08 | P4 | `feature/db-08-query-perf` | Query performance audit | - |

## BE - Backend (FastAPI)

| ID | Phase | Branch | Task | Depends on |
|---|---|---|---|---|
| BE-01 | P0 | `feature/be-01-fastapi-skeleton` | FastAPI skeleton | - |
| BE-02 | P1 | `feature/be-02-auth-jwt` | Registration & login (JWT) | DB-02 |
| BE-03 | P1 | `feature/be-03-oauth` | OAuth 2.0 login | BE-02 |
| BE-04 | P1 | `feature/be-04-profile` | User profile API | BE-02 |
| BE-05 | P1 | `feature/be-05-websocket-core` | WebSocket core | BE-02 |
| BE-06 | P2 | `feature/be-06-matchmaking-queue` | Matchmaking queue | BE-05, BE-04 |
| BE-07 | P2 | `feature/be-07-chat-session` | Chat session lifecycle | BE-06 |
| BE-08 | P2 | `feature/be-08-messages` | Real-time messaging | BE-07 |
| BE-09 | P2 | `feature/be-09-file-upload` | File, media & voice upload | BE-08 |
| BE-10 | P3 | `feature/be-10-api-keys-ratelimit` | API keys & rate limiting | DB-02 |
| BE-11 | P3 | `feature/be-11-public-api` | Public API (5+ endpoints) | BE-10 |
| BE-12 | P3 | `feature/be-12-public-api-docs` | Public API documentation | BE-11 |
| BE-13 | P4 | `feature/be-13-translation` | Auto-translation (optional) | BE-08 |
| BE-14 | P4 | `feature/be-14-tests` | Backend tests | - |

## FE1 - Frontend: account & social

| ID | Phase | Branch | Task | Depends on |
|---|---|---|---|---|
| FE1-01 | P0 | `feature/fe1-01-vite-skeleton` | Vite + React + TS skeleton | - |
| FE1-02 | P1 | `feature/fe1-02-auth-pages` | Login & registration pages | BE-02 |
| FE1-03 | P1 | `feature/fe1-03-oauth-buttons` | OAuth buttons & callback page | BE-03 |
| FE1-04 | P1 | `feature/fe1-04-profile` | Profile setup & profile page | BE-04, BE-09 |
| FE1-05 | P2 | `feature/fe1-05-dashboard` | Main dashboard | - |
| FE1-06 | P3 | `feature/fe1-06-friends-ui` | Friends UI | DB-04 |
| FE1-07 | P3 | `feature/fe1-07-notifications-ui` | Notifications UI | DB-05 |
| FE1-08 | P3 | `feature/fe1-08-admin-dashboard` | Admin analytics dashboard | DB-07 |
| FE1-09 | P4 | `feature/fe1-09-i18n-settings` | Settings, i18n, API keys page | BE-10 |

## FE2 - Frontend: matchmaking & chat

| ID | Phase | Branch | Task | Depends on |
|---|---|---|---|---|
| FE2-01 | P0 | `feature/fe2-01-ui-kit` | UI kit | - |
| FE2-02 | P1 | `feature/fe2-02-ws-client` | WebSocket client & hook | BE-05 |
| FE2-03 | P2 | `feature/fe2-03-matchmaking-ui` | Matchmaking page | BE-06 |
| FE2-04 | P2 | `feature/fe2-04-chat-ui` | Chat interface | BE-07, BE-08 |
| FE2-05 | P2 | `feature/fe2-05-media-voice` | Files & voice messages UI | BE-09 |
| FE2-06 | P3 | `feature/fe2-06-search-ui` | Partner search UI | DB-06 |
| FE2-07 | P4 | `feature/fe2-07-translation-ui` | Auto-translation toggle (optional) | BE-13 |
| FE2-08 | P4 | `feature/fe2-08-cross-browser` | Cross-browser fixes | OPS-08 |

## Critical path

`DB-01 -> DB-02 -> BE-02 -> BE-05 -> BE-06 -> BE-07 -> BE-08` (backend core) in parallel with `FE1-01 / FE2-01 -> FE2-02 -> FE2-03 -> FE2-04` (frontend on mocks).
Agree in week 1 on `docs/WS_PROTOCOL.md` (BE + FE2) and the OpenAPI schema (BE + FE1).

## Definition of done

- Work lives on a `feature/*` branch, PR into `develop`, at least 1 approval, CI green.
- No secrets in code; migrations included when the schema changes.
- Endpoints appear in OpenAPI; UI works at mobile width.
