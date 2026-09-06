from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from tools.dev.config import WORKSPACE_ROOT


REPOSITORIES = (
    ("backend", WORKSPACE_ROOT / "pingou-o-que-backend", "BACKEND_PATH"),
    ("frontend", WORKSPACE_ROOT / "pingou-o-que-frontend", "FRONTEND_PATH"),
    ("landing", WORKSPACE_ROOT / "pingou-o-que-landing-page", "LANDING_PATH"),
    ("chat", WORKSPACE_ROOT / "pingou-o-que-chat", "CHAT_PATH"),
)


def git_worktrees(repository: Path) -> list[tuple[Path, str]]:
    result = subprocess.run(
        ["git", "-C", str(repository), "worktree", "list", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    worktrees: list[tuple[Path, str]] = []
    path: Path | None = None
    branch = "detached"
    for line in (*result.stdout.splitlines(), ""):
        if not line:
            if path is not None:
                worktrees.append((path.resolve(), branch))
            path = None
            branch = "detached"
            continue

        key, _, value = line.partition(" ")
        if key == "worktree":
            path = Path(value)
        elif key == "branch":
            branch = value.removeprefix("refs/heads/")

    return worktrees


def environment_files() -> list[Path]:
    files = [
        path
        for path in WORKSPACE_ROOT.glob(".env*")
        if path.is_file() and path.name != ".env.example"
    ]
    return sorted(files, key=lambda path: (path.name != ".env", path.name))


def selected_paths(env_file: Path) -> dict[str, Path]:
    selected: dict[str, Path] = {}
    allowed_keys = {env_key for _, _, env_key in REPOSITORIES}

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in allowed_keys:
            continue

        path = Path(value.strip().strip('"').strip("'"))
        if not path.is_absolute():
            path = WORKSPACE_ROOT / path
        selected[key] = path.resolve()

    return selected


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    repositories = {
        label: git_worktrees(path)
        for label, path, _ in REPOSITORIES
    }
    known_worktrees = {
        label: {worktree_path: branch for worktree_path, branch in worktrees}
        for label, worktrees in repositories.items()
    }
    referenced: set[Path] = set()
    env_files = environment_files()

    if not env_files:
        raise SystemExit(
            "No .env files found. Create one with `make env-init ENV_NAME=<name>`."
        )

    print("Worktree environments")
    for env_file in env_files:
        print(f"\n{env_file.name}")
        configured = selected_paths(env_file)
        for label, repository, env_key in REPOSITORIES:
            selected = configured.get(env_key, repository.resolve())
            branch = known_worktrees[label].get(selected)
            if branch is None:
                print(f"  {label:8} unavailable ({env_key} does not select a Git worktree)")
                continue

            referenced.add(selected)
            print(f"  {label:8} {branch:36} {display_path(selected)}")

        command = f"make up ENV_FILE={shlex.quote(env_file.name)}"
        print(f"  Run: {command}")

    unconfigured: list[tuple[str, str, Path]] = []
    workspace_worktrees = git_worktrees(WORKSPACE_ROOT)
    for path, branch in workspace_worktrees[1:]:
        unconfigured.append(("workspace", branch, path))
    for label, worktrees in repositories.items():
        for path, branch in worktrees[1:]:
            if path not in referenced:
                unconfigured.append((label, branch, path))

    if unconfigured:
        print("\nLinked worktrees without a root environment")
        for label, branch, path in unconfigured:
            print(f"  {label:8} {branch:36} {display_path(path)}")


if __name__ == "__main__":
    main()
