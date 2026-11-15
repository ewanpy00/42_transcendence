# Development workflow

Short version: **pick your issue -> create `feature/*` branch from `develop` -> commit -> open PR into `develop` -> owner approves -> squash merge.**

## Branch model

```
main        <- stable, releases only (owner merges develop into main)
develop     <- integration branch, all PRs target it
feature/*   <- one branch per issue, created by the developer
fix/*       <- bug fixes outside of an issue
```

- `main` and `develop` are protected: **no direct pushes**, every change goes through a PR.
- Every PR needs **1 approval from the repository owner** (`@ewanpy00`, see `.github/CODEOWNERS`).
- Feature branches are **not** pre-created. You create yours when you start a task.

## Step by step

### 1. Pick a task
- Work only on issues **assigned to you** (see [docs/ISSUES.md](docs/ISSUES.md) or the GitHub issue list).
- Start with the lowest phase (P0 -> P4) and check **Depends on** in the issue. If a dependency is not merged yet, you may start against mocks, but your PR cannot be merged before it.
- Comment "starting" on the issue so the team sees what is in progress.

### 2. Create the branch
Use the exact branch name from the issue body, e.g. `feature/be-06-matchmaking-queue`.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/be-06-matchmaking-queue
```

One issue = one branch = one PR. Do not mix several issues in one branch.

### 3. Work and commit
- Commit small and often, using Conventional Commits:
  `feat(matchmaking): add queue join endpoint`, `fix(chat): handle empty message`, `docs: ...`, `test: ...`, `chore: ...`.
- Stay inside your folders (see ownership below). If you must change someone else's code, mention the owner in the PR.
- Never commit secrets (`.env`, keys, tokens). Use `.env.example` for new variables.
- Schema change? Include the Alembic migration and tell the DB owner.

### 4. Keep up to date with develop
Before opening a PR, and whenever `develop` moves a lot:

```bash
git fetch origin
git rebase origin/develop      # or: git merge origin/develop
```

Resolve conflicts locally, never in the PR.

### 5. Push and open a PR

```bash
git push -u origin feature/be-06-matchmaking-queue
```

Open a PR **into `develop`** (never into `main`):
- Title: `[BE-06] Matchmaking queue` (issue ID + issue title).
- Description: fill the PR template, include `Closes #<issue number>`.
- Keep PRs small and focused; if it grows beyond ~400 changed lines, split the work.
- Self-review your diff first. Make sure CI is green.

### 6. Review
- The owner reviews and approves, or requests changes.
- Push fixes to the same branch (new commits dismiss the old approval, that is expected).
- Reply to every review comment; do not resolve other people's comments for them.

### 7. Merge and clean up
- Merge with **Squash and merge** after approval and green CI.
- Delete the branch after merging.
- Move on: `git checkout develop && git pull`, then take the next issue.

## Releases
When `develop` is stable (e.g. end of a phase), the owner opens a PR `develop` -> `main`.

## Folder ownership

| Folder | Owner |
|---|---|
| `backend/app/{api,core,ws,services,schemas}` | BE |
| `backend/app/{models,db}`, `backend/alembic`, `backend/app/services/{search,analytics,notifications}.py` | DB |
| `docker-compose.yml`, `deploy/`, `nginx/`, `.github/workflows`, `cli/`, `scripts/` | OPS |
| `frontend/src/features/{auth,profile,friends,notifications,admin}`, dashboard/profile/admin pages | FE1 |
| `frontend/src/features/{matchmaking,chat,search}`, `hooks/`, `components/ui` | FE2 |

## Rules of thumb
- Blocked or unsure? Comment on the issue and tag the owner of the dependency.
- Found a bug in someone else's area? Open a new issue, do not fix it silently.
- Change the API or WebSocket contract? Update `docs/` and tell the affected frontend/backend dev in the PR.
- Never force-push to a branch someone else is using. Force-pushing your own feature branch after a rebase is fine.
