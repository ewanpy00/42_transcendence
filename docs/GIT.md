# Git cheat sheet

Feature flow: **branch from `develop` -> commit -> push -> PR into `develop`** (details: [CONTRIBUTING.md](../CONTRIBUTING.md)).

```bash
# 1. start
git checkout develop && git pull origin develop
git checkout -b feature/be-01-fastapi-skeleton     # name from the issue

# 2. work
git add <files>
git commit -m "feat(api): add FastAPI skeleton"    # Conventional Commits

# 3. sync with develop before the PR
git fetch origin
git rebase origin/develop

# 4. publish + PR
git push -u origin feature/be-01-fastapi-skeleton  # after a rebase: git push --force-with-lease
gh pr create --base develop --title "[BE-01] FastAPI skeleton" --body "Closes #17"

# 5. after squash merge
git checkout develop && git pull origin develop
git branch -d feature/be-01-fastapi-skeleton
```

## Handy extras

| Need | Command |
|---|---|
| Pull latest `develop` into your branch (no rebase) | `git merge origin/develop` |
| Continue / abort a rebase | `git rebase --continue` / `git rebase --abort` |
| Unstage / undo last commit (keep changes) | `git restore --staged <file>` / `git reset --soft HEAD~1` |
| Park changes temporarily | `git stash` / `git stash pop` |
| Fix last commit message or add forgotten file | `git add <file> && git commit --amend` |
| See state / history | `git status` / `git log --oneline --graph -10` |

Never push directly to `main` or `develop`; never force-push shared branches.
