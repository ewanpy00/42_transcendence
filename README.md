# Transcendence

A language-practice chat platform: a user (Teacher / Student) joins a queue, gets matched with a partner by filters (role, age, gender) and chats in real time (text, files, voice messages).

**Stack:** React (Vite, TypeScript) · FastAPI · SQLAlchemy + Alembic · PostgreSQL · WebSockets · Docker Compose · nginx

## Structure

```
backend/    FastAPI app (api, ws, services, models, alembic)
frontend/   React SPA (feature-based)
cli/        CLI built on the public API
deploy/     nginx, backups, monitoring
docs/       architecture, DB schema, API, issues
scripts/    helper scripts (issue generation, etc.)
```

## Quick start

```bash
cp .env.example .env
make up        # available after OPS-01
```

## Docs

- [docs/ISSUES.md](docs/ISSUES.md) - tasks per developer
- [CONTRIBUTING.md](CONTRIBUTING.md) - branches, PRs, folder ownership
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - architecture and module map
