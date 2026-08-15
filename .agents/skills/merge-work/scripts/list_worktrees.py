#!/usr/bin/env python3
"""List linked worktrees across the Pingou workspace and whether they can merge."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CHILD_REPOS = (
    "pingou-o-que-backend",
    "pingou-o-que-frontend",
    "pingou-o-que-landing-page",
    "pingou-o-que-chat",
)


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[4]


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def base_branch(repo: Path) -> str:
    result = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if result.returncode == 0:
        ref = result.stdout.strip()
        prefix = "refs/remotes/origin/"
        if ref.startswith(prefix):
            return ref[len(prefix) :]

    for candidate in ("main", "master"):
        listed = git(repo, "branch", "--list", candidate)
        if listed.stdout.strip():
            return candidate
    return "main"


def parse_worktrees(repo: Path) -> list[dict[str, str]]:
    result = git(repo, "worktree", "list", "--porcelain")
    if result.returncode != 0:
        return []

    trees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in result.stdout.splitlines():
        line = raw.rstrip()
        if not line:
            if current:
                trees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = value
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "detached":
            current["branch"] = "DETACHED"
        elif key == "prunable":
            current["prunable"] = "yes"
    if current:
        trees.append(current)
    return trees


def is_dirty(path: Path) -> bool:
    if not path.exists():
        return False
    result = git(path, "status", "--porcelain")
    return bool(result.stdout.strip())


def is_merged(repo: Path, branch: str, base: str) -> bool:
    result = git(repo, "merge-base", "--is-ancestor", branch, base)
    return result.returncode == 0


def repo_rows(name: str, repo: Path) -> list[str]:
    if not repo.is_dir() or not (repo / ".git").exists():
        return [f"{name:24} SKIP missing checkout"]

    base = base_branch(repo)
    rows = [f"{name}  base={base}  path={repo}"]
    trees = parse_worktrees(repo)
    if not trees:
        rows.append("  (no worktrees reported)")
        return rows

    primary = trees[0]["path"]
    for tree in trees:
        path = tree.get("path", "")
        branch = tree.get("branch", "DETACHED")
        prunable = tree.get("prunable") == "yes"
        linked = path != primary
        if not linked:
            dirty = is_dirty(Path(path))
            rows.append(
                f"  primary  {branch:40} dirty={str(dirty).lower():5} {path}"
            )
            continue

        missing = not Path(path).exists()
        dirty = False if missing or prunable else is_dirty(Path(path))
        merged = (
            False
            if branch == "DETACHED" or missing or prunable
            else is_merged(repo, branch, base)
        )
        if prunable or missing:
            action = "prune"
        elif branch == "DETACHED":
            action = "skip-detached"
        elif dirty:
            action = "skip-dirty"
        elif merged:
            action = "already-merged"
        else:
            action = "merge-and-push"
        rows.append(
            f"  {action:16} {branch:40} dirty={str(dirty).lower():5} {path}"
        )
    return rows


def main() -> int:
    root = workspace_root()
    print(f"workspace {root}")
    print()
    for line in repo_rows("pingou-o-que", root):
        print(line)
    print()
    for name in CHILD_REPOS:
        for line in repo_rows(name, root / name):
            print(line)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
