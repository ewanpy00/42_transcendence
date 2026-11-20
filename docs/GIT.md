# Git cheat sheet

Feature flow: **branch from `develop` -> commit -> push -> PR into `develop`** (details: [CONTRIBUTING.md](../CONTRIBUTING.md)).

## 1. Start a task

| Command | Why |
|---|---|
| `git checkout develop && git pull origin develop` | Switch to `develop` and fetch the latest changes, so the new branch starts from fresh code. |
| `git checkout -b feature/be-01-fastapi-skeleton` | Create and switch to your feature branch (name comes from the issue). |

## 2. Work and commit

| Command | Why |
|---|---|
| `git status` | Show which files changed and what is staged. |
| `git add <files>` | Stage the files that should go into the next commit. |
| `git commit -m "feat(api): add FastAPI skeleton"` | Save the staged changes as a commit (Conventional Commits: `feat`, `fix`, `docs`, `test`, `chore`). |

## 3. Sync with develop (before the PR)

| Command | Why |
|---|---|
| `git fetch origin` | Download new commits from GitHub without changing your files. |
| `git rebase origin/develop` | Replay your commits on top of the latest `develop` for a clean linear history. |
| `git merge origin/develop` | Alternative to rebase: merge `develop` into your branch (adds a merge commit). |
| `git rebase --continue` | Proceed with the rebase after you resolved a conflict and ran `git add`. |
| `git rebase --abort` | Cancel the rebase and return to the state before it. |

## 4. Publish and open a PR

| Command | Why |
|---|---|
| `git push -u origin feature/be-01-fastapi-skeleton` | Upload the branch to GitHub and link it to the remote (first push). |
| `git push --force-with-lease` | Push after a rebase (history changed); safer than `--force`, refuses if someone else pushed meanwhile. |
| `gh pr create --base develop --title "[BE-01] FastAPI skeleton" --body "Closes #17"` | Open a PR into `develop`; `Closes #17` auto-closes the issue on merge. |

## 5. After the squash merge

| Command | Why |
|---|---|
| `git checkout develop && git pull origin develop` | Go back to `develop` and get the merged result. |
| `git branch -d feature/be-01-fastapi-skeleton` | Delete the local feature branch, it is no longer needed. |

## Handy extras

| Command | Why |
|---|---|
| `git restore --staged <file>` | Unstage a file (changes stay in the working tree). |
| `git reset --soft HEAD~1` | Undo the last commit but keep its changes staged. |
| `git stash` / `git stash pop` | Temporarily put uncommitted changes aside / bring them back (e.g. to switch branches). |
| `git add <file> && git commit --amend` | Add a forgotten file or fix the message of the last commit (before pushing). |
| `git log --oneline --graph -10` | Compact view of recent history. |

Never push directly to `main` or `develop`; never force-push shared branches.
