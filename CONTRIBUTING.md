# Contributing

## Branches

```
main        <- stable, releases only (merged from develop)
develop     <- integration branch, all PRs target it
feature/*   <- one branch per issue
fix/*       <- bug fixes
```

Branch name: `feature/<id>-<slug>`, e.g. `feature/be-06-matchmaking-queue`.
IDs come from [docs/ISSUES.md](docs/ISSUES.md) and match GitHub issue titles (`[BE-06] ...`).

```bash
git checkout develop && git pull
git checkout -b feature/be-06-matchmaking-queue
# ... work ...
git push -u origin feature/be-06-matchmaking-queue   # then open a PR into develop
```

## Commits (Conventional Commits)

`feat(matchmaking): add queue join endpoint`, `fix(chat): ...`, `docs: ...`, `chore: ...`, `test: ...`.

## Pull requests

- Title: `[BE-06] Matchmaking queue`; description contains `Closes #<issue>`.
- At least 1 review from another team member and green CI.
- Merge strategy: squash. Delete the branch after merging.
- No direct pushes to `main` or `develop` (enable branch protection).

## Folder ownership

| Folder | Owner |
|---|---|
| `backend/app/{api,core,ws,services,schemas}` | BE |
| `backend/app/{models,db}`, `backend/alembic`, `backend/app/services/{search,analytics,notifications}.py` | DB |
| `docker-compose.yml`, `deploy/`, `.github/workflows`, `cli/`, `scripts/` | OPS |
| `frontend/src/features/{auth,profile,friends,notifications,admin}`, dashboard/profile/admin pages | FE1 |
| `frontend/src/features/{matchmaking,chat,search}`, `hooks/`, `components/ui` | FE2 |

If you touch someone else's folder, mention the owner in the PR to avoid conflicts.
