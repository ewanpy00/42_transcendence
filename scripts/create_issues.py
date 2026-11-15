#!/usr/bin/env python3
"""Create labels and GitHub issues from issues_data.py using the gh CLI.

Usage: python3 scripts/create_issues.py [--repo owner/name] [--dry-run]
Re-running skips issues whose "[ID]" prefix already exists in the repo.
"""
import argparse
import json
import subprocess
import sys

from issues_data import ISSUES, PHASES, ROLES, body

COLORS = {"role": "1d76db", "phase": "5319e7", "optional": "bfdadc"}


def gh(*args, repo=None, check=True):
    cmd = ["gh", *args] + (["--repo", repo] if repo else [])
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="ewanpy00/42_transcendence")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.dry_run:
        for _, (name, label) in ROLES.items():
            gh("label", "create", label, "--color", COLORS["role"], "--description", name, "--force", repo=a.repo)
        for p, name in PHASES.items():
            gh("label", "create", f"phase:{p.lower()}", "--color", COLORS["phase"], "--description", name, "--force", repo=a.repo)
        gh("label", "create", "optional", "--color", COLORS["optional"], "--force", repo=a.repo)
        out = gh("issue", "list", "--state", "all", "--limit", "500", "--json", "title", repo=a.repo).stdout
        existing = {t["title"] for t in json.loads(out)}
    else:
        existing = set()

    for i in ISSUES:
        iid, phase, _, title, *_ = i
        full = f"[{iid}] {title}"
        if full in existing:
            print(f"skip   {full}")
            continue
        labels = [ROLES[iid.split("-")[0]][1], f"phase:{phase.lower()}"]
        if "optional" in title.lower():
            labels.append("optional")
        if a.dry_run:
            print(f"dry    {full} {labels}")
            continue
        r = gh("issue", "create", "--title", full, "--body", body(i), "--label", ",".join(labels), repo=a.repo, check=False)
        print(("ok     " if r.returncode == 0 else "FAILED ") + full, r.stdout.strip() or r.stderr.strip())
        if r.returncode:
            sys.exit(1)


if __name__ == "__main__":
    main()
