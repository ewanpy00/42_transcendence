"""Single source of truth for project issues.

Used by:
  python3 scripts/issues_data.py markdown   -> regenerates docs/ISSUES.md
  python3 scripts/create_issues.py          -> creates labels + GitHub issues via gh
"""

ROLES = {
    "OPS": ("Deploy / DevOps", "role:ops"),
    "DB": ("Database + data-heavy API", "role:db"),
    "BE": ("Backend (FastAPI)", "role:be"),
    "FE1": ("Frontend: account & social", "role:fe1"),
    "FE2": ("Frontend: matchmaking & chat", "role:fe2"),
}

PHASES = {
    "P0": "Foundation",
    "P1": "Core (auth, profile, WebSocket)",
    "P2": "Matchmaking & chat",
    "P3": "Social features & modules",
    "P4": "Polish",
}

# (id, phase, slug, title, description, deps, acceptance criteria)
ISSUES = [
    # ---------------- OPS ----------------
    ("OPS-01", "P0", "docker-compose", "Docker Compose setup",
     "Postgres, redis and nginx already exist in `docker-compose.yml`. Add backend and frontend services (Dockerfiles), wire nginx upstreams, and make backend wait for healthy postgres.",
     [], ["`make up` starts the whole stack (postgres, redis, backend, frontend, nginx)", "Healthchecks, named volumes and a shared network", "Backend waits for a healthy database"]),
    ("OPS-02", "P0", "env-secrets", "Environment & secrets management",
     "Provide `.env.example`, load env into containers, keep secrets out of git, document startup in README.",
     [], ["No secrets committed", "README describes first-run steps"]),
    ("OPS-03", "P0", "ci", "CI pipeline (GitHub Actions)",
     "Lint and test backend (ruff, pytest); lint and build frontend. Run on every PR.",
     [], ["CI runs on PRs to develop/main", "Failing lint/test blocks merge"]),
    ("OPS-04", "P1", "nginx-https", "nginx reverse proxy with HTTPS",
     "`/` -> frontend, `/api` -> backend, `/ws` with upgrade headers, self-signed HTTPS, serve `/uploads`.",
     ["OPS-01"], ["HTTPS works locally", "WebSocket connections pass through nginx"]),
    ("OPS-05", "P3", "healthcheck-status", "Health check & status page",
     "`/health` (liveness) and `/status` (db, websocket, disk) plus a simple status page.",
     ["BE-01"], ["Status page shows component states", "Docker healthchecks use the endpoints"]),
    ("OPS-06", "P3", "backup-dr", "Automated backups & disaster recovery",
     "Scheduled postgres backups with rotation, `restore.sh`, disaster recovery document, verified restore.",
     ["DB-02"], ["Backups run automatically", "Restore tested end-to-end", "DR procedure documented in docs/"]),
    ("OPS-07", "P3", "cli", "CLI for the public API",
     "CLI in `cli/` built on the public API using an API key (e.g. list/get users, queue stats).",
     ["BE-11"], ["CLI authenticates with API key", "At least 3 commands documented"]),
    ("OPS-08", "P4", "browser-support", "Browser support matrix",
     "Test on Chrome, Firefox and Safari/Edge; manual + automated smoke runs; hand a bug list to FE.",
     [], ["Matrix documented", "Bugs filed for FE2-08"]),

    # ---------------- DB ----------------
    ("DB-01", "P0", "schema-design", "Database schema design & ERD",
     "ERD and `docs/DB_SCHEMA.md`: users, friendships, queue_entries, chat_sessions, messages, files, notifications, api_keys, activity_log. Plan indexes for search. Agree with BE.",
     [], ["ERD committed", "Reviewed by BE"]),
    ("DB-02", "P0", "models-alembic", "SQLAlchemy models & Alembic",
     "Models in `backend/app/models`, `db/base.py`, `db/session.py`, Alembic setup and initial migration.",
     ["DB-01"], ["`alembic upgrade head` works on empty DB", "Downgrade works"]),
    ("DB-03", "P1", "seed-data", "Seed data script",
     "Seed 50+ users with varied ages/languages/roles, friendships and messages for dev and demo.",
     ["DB-02"], ["Idempotent seed command", "Documented in README"]),
    ("DB-04", "P2", "friends", "Friends system API",
     "Send/accept/decline/remove friend requests, list friends, block users.",
     ["BE-02"], ["All transitions covered", "Cannot friend yourself or duplicate"]),
    ("DB-05", "P3", "notifications", "Notification system",
     "Notifications for create/update/delete events (friend, message, profile, file); storage, read/unread, push via WebSocket.",
     ["BE-05"], ["Events generate notifications", "Real-time delivery", "Mark read / delete"]),
    ("DB-06", "P3", "search", "Advanced search with filters, sorting, pagination",
     "Partner search by age, language, role, gender; sorting; limit/offset or cursor pagination; supporting indexes.",
     ["DB-02"], ["All filters combinable", "Pagination metadata returned", "Indexes in migration"]),
    ("DB-07", "P3", "analytics", "User activity analytics",
     "DAU, signups, chat counts, average chat duration, queue stats; activity_log; `/admin/stats` endpoints.",
     ["DB-02"], ["Admin-only access", "Queries performant on seed data"]),
    ("DB-08", "P4", "query-perf", "Query performance audit",
     "EXPLAIN audit of hot queries, add missing indexes, migration up/down tests.",
     [], ["Slow queries documented and fixed"]),

    # ---------------- BE ----------------
    ("BE-01", "P0", "fastapi-skeleton", "FastAPI skeleton",
     "`main.py`, pydantic-settings config, CORS, v1 routers, error handling, OpenAPI, `/health`.",
     [], ["App starts in container", "Swagger UI available"]),
    ("BE-02", "P1", "auth-jwt", "Registration & login (JWT)",
     "Register/login, password hashing, JWT access + refresh, `get_current_user`, logout.",
     ["DB-02"], ["Passwords hashed", "Refresh flow works", "Protected route example"]),
    ("BE-03", "P1", "oauth", "OAuth 2.0 login",
     "Google and GitHub (and 42 if possible): callback handling, create or link user.",
     ["BE-02"], ["Login via at least 2 providers", "Existing accounts linked by email"]),
    ("BE-04", "P1", "profile", "User profile API",
     "Age, gender, role (teacher/student), language, bio; GET/PATCH `/users/me`, public profile; validation.",
     ["BE-02"], ["Validation errors are clear", "Role is required before matchmaking"]),
    ("BE-05", "P1", "websocket-core", "WebSocket core",
     "ConnectionManager, JWT auth for sockets, heartbeat, event protocol documented in `docs/WS_PROTOCOL.md`.",
     ["BE-02"], ["Unauthorized sockets rejected", "Protocol doc agreed with FE2"]),
    ("BE-06", "P2", "matchmaking-queue", "Matchmaking queue",
     "Join/cancel queue, preferences (role/Random, age range, gender), matching algorithm, remove from queue on match/cancel/disconnect, queue status over WS.",
     ["BE-05", "BE-04"], ["Compatible users are matched", "No user is in the queue twice", "Queue cleaned on disconnect"]),
    ("BE-07", "P2", "chat-session", "Chat session lifecycle",
     "States Waiting/Connected/Disconnected, skip, leave, automatic disconnect handling with grace period, re-queue after skip.",
     ["BE-06"], ["State transitions enforced", "Partner notified on leave/disconnect"]),
    ("BE-08", "P2", "messages", "Real-time messaging",
     "One-to-one text messages over WS, persistence, history, sync, partner info.",
     ["BE-07"], ["Messages delivered and stored", "History endpoint paginated"]),
    ("BE-09", "P2", "file-upload", "File, media & voice upload",
     "Upload with type/size validation, storage, serving, deletion, linking to messages and avatars.",
     ["BE-08"], ["Invalid types rejected", "Files removed with their message/user"]),
    ("BE-10", "P3", "api-keys-ratelimit", "API keys & rate limiting",
     "Hashed API key model, create/revoke, `require_api_key` dependency, rate limiting.",
     ["DB-02"], ["Keys shown once", "429 on limit exceeded"]),
    ("BE-11", "P3", "public-api", "Public API (5+ endpoints)",
     "Public API under `/public/v1` with GET/POST/PUT/DELETE, secured by API key, documented in Swagger.",
     ["BE-10"], ["At least 5 endpoints", "All require API key and are rate limited"]),
    ("BE-12", "P3", "public-api-docs", "Public API documentation",
     "`docs/API.md` with curl examples and versioning notes.",
     ["BE-11"], ["Every public endpoint documented with example"]),
    ("BE-13", "P4", "translation", "Auto-translation (optional)",
     "Translate messages to the user's language: service wrapper, cache, profile flag.",
     ["BE-08"], ["Toggle per user", "Cached translations"]),
    ("BE-14", "P4", "tests", "Backend tests",
     "Unit and integration tests for auth, matchmaking, chat lifecycle.",
     [], ["Key flows covered", "Runs in CI"]),

    # ---------------- FE1 ----------------
    ("FE1-01", "P0", "vite-skeleton", "Vite + React + TS skeleton",
     "Router, `src/` structure, layout with navigation, API client, protected routes.",
     [], ["`npm run dev` and build work", "Protected route redirects to login"]),
    ("FE1-02", "P1", "auth-pages", "Login & registration pages",
     "Forms, validation, token storage, automatic refresh.",
     ["BE-02"], ["Mock API until backend is ready", "Errors displayed"]),
    ("FE1-03", "P1", "oauth-buttons", "OAuth buttons & callback page",
     "Google/GitHub/42 buttons and callback handling.",
     ["BE-03"], ["Login completes and redirects"]),
    ("FE1-04", "P1", "profile", "Profile setup & profile page",
     "Setup wizard (age, gender, Teacher/Student, language), profile page, editing, avatar.",
     ["BE-04", "BE-09"], ["New users forced through setup", "Edit and avatar upload work"]),
    ("FE1-05", "P2", "dashboard", "Main dashboard",
     "Greeting, quick start search, online friends, recent chats.",
     [], ["Responsive", "Links to matchmaking and profile"]),
    ("FE1-06", "P3", "friends-ui", "Friends UI",
     "Friend list, requests, add/remove, friend profile.",
     ["DB-04"], ["All friend actions available"]),
    ("FE1-07", "P3", "notifications-ui", "Notifications UI",
     "Bell, list, read/unread, real-time toasts.",
     ["DB-05"], ["Live updates via WS"]),
    ("FE1-08", "P3", "admin-dashboard", "Admin analytics dashboard",
     "Charts for stats and activity.",
     ["DB-07"], ["Admin-only route", "Charts render with seed data"]),
    ("FE1-09", "P4", "i18n-settings", "Settings, i18n, API keys page",
     "Interface language, theme, i18n scaffolding, API key management page.",
     ["BE-10"], ["At least 2 UI languages", "Create/revoke API keys"]),

    # ---------------- FE2 ----------------
    ("FE2-01", "P0", "ui-kit", "UI kit",
     "Button, Input, Select, Modal, Avatar, Toast, Spinner, design tokens, responsive. Agree with FE1.",
     [], ["Components documented", "Used by both FE devs"]),
    ("FE2-02", "P1", "ws-client", "WebSocket client & hook",
     "`useSocket`: token connect, reconnect with backoff, event subscriptions, context.",
     ["BE-05"], ["Reconnect works", "Typed events"]),
    ("FE2-03", "P2", "matchmaking-ui", "Matchmaking page",
     "Filters (role/age/gender), Find/Cancel, queue status, redirect to chat on match.",
     ["BE-06"], ["Cancel removes from queue", "Match opens chat"]),
    ("FE2-04", "P2", "chat-ui", "Chat interface",
     "Message list, input, partner card, session states, Skip/Leave, disconnect handling.",
     ["BE-07", "BE-08"], ["Skip returns to queue", "Disconnect shown clearly"]),
    ("FE2-05", "P2", "media-voice", "Files & voice messages UI",
     "File/image send with preview and progress, voice recording (MediaRecorder), audio player.",
     ["BE-09"], ["Voice record/send/play works", "Upload errors handled"]),
    ("FE2-06", "P3", "search-ui", "Partner search UI",
     "Filters, sorting, pagination.",
     ["DB-06"], ["URL reflects filters"]),
    ("FE2-07", "P4", "translation-ui", "Auto-translation toggle (optional)",
     "Switch to translate incoming messages.",
     ["BE-13"], ["Toggle persists"]),
    ("FE2-08", "P4", "cross-browser", "Cross-browser fixes",
     "Fix Firefox/Safari issues (MediaRecorder, WS, CSS) from OPS-08 report.",
     ["OPS-08"], ["No blocking bugs on supported browsers"]),
]


def branch(issue):
    return f"feature/{issue[0].lower()}-{issue[2]}"


def body(issue):
    iid, phase, slug, title, desc, deps, crit = issue
    lines = [desc, "", f"**Branch:** `{branch(issue)}`", f"**Phase:** {phase} - {PHASES[phase]}"]
    lines.append("**Depends on:** " + (", ".join(deps) if deps else "none"))
    lines += ["", "## Acceptance criteria"] + [f"- [ ] {c}" for c in crit]
    lines += ["", "_Branch from `develop`, open a PR back into `develop`. See CONTRIBUTING.md._"]
    return "\n".join(lines)


def markdown():
    out = ["# Issues by developer", "",
           "_Generated from `scripts/issues_data.py`. Do not edit by hand._", "",
           "Roles: **BE** backend, **DB** database + data-heavy API, **OPS** deploy/devops, **FE1**/**FE2** frontend.",
           "One issue = one branch (`feature/<id>-<slug>` from `develop`) = one PR.",
           "Dependencies mean: do not merge before the dependency (you can start earlier against mocks).", ""]
    out += ["Phases: " + " -> ".join(f"**{k}** {v}" for k, v in PHASES.items()), ""]
    for role, (name, _) in ROLES.items():
        out += [f"## {role} - {name}", "", "| ID | Phase | Branch | Task | Depends on |", "|---|---|---|---|---|"]
        for i in ISSUES:
            if i[0].startswith(role + "-"):
                out.append(f"| {i[0]} | {i[1]} | `{branch(i)}` | {i[3]} | {', '.join(i[5]) or '-'} |")
        out.append("")
    out += ["## Critical path", "",
            "`DB-01 -> DB-02 -> BE-02 -> BE-05 -> BE-06 -> BE-07 -> BE-08` (backend core) in parallel with "
            "`FE1-01 / FE2-01 -> FE2-02 -> FE2-03 -> FE2-04` (frontend on mocks).",
            "Agree in week 1 on `docs/WS_PROTOCOL.md` (BE + FE2) and the OpenAPI schema (BE + FE1).", "",
            "## Definition of done", "",
            "- Work lives on a `feature/*` branch, PR into `develop`, at least 1 approval, CI green.",
            "- No secrets in code; migrations included when the schema changes.",
            "- Endpoints appear in OpenAPI; UI works at mobile width.", ""]
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["markdown"]:
        open("docs/ISSUES.md", "w").write(markdown())
        print("docs/ISSUES.md written")
