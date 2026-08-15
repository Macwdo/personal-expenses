from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import tempfile
from pathlib import Path

from tools.dev.config import PortlessConfig, WORKSPACE_ROOT, resolve_env_file


def environment_name(explicit_name: str | None) -> str:
    if explicit_name:
        return explicit_name

    result = subprocess.run(
        ["git", "-C", str(WORKSPACE_ROOT), "branch", "--show-current"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or WORKSPACE_ROOT.name


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", value.lower().replace("_", "-"))
    return slug.strip("-")[:32] or "worktree"


def project_name(name: str) -> str:
    checksum = hashlib.sha256(str(WORKSPACE_ROOT.resolve()).encode()).hexdigest()[:8]
    return f"pingou-{slugify(name)}-{checksum}"


def replace_values(template: str, replacements: dict[str, str]) -> str:
    pending = set(replacements)
    output: list[str] = []

    for line in template.splitlines():
        key = line.split("=", 1)[0] if "=" in line else ""
        if key in replacements:
            output.append(f"{key}={replacements[key]}")
            pending.remove(key)
        else:
            output.append(line)

    if pending:
        missing = ", ".join(sorted(pending))
        raise ValueError(f"missing keys in .env.example: {missing}")

    return "\n".join(output) + "\n"


def write_exclusive(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(
            f"refusing to overwrite existing environment file: {destination}"
        )

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=destination.parent,
        prefix=f"{destination.name}.",
        delete=False,
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)

    try:
        os.link(temporary_path, destination)
    except FileExistsError:
        raise FileExistsError(
            f"refusing to overwrite existing environment file: {destination}"
        ) from None
    finally:
        temporary_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a worktree-local Compose environment file."
    )
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--env-name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = resolve_env_file(args.env_file)
    project = project_name(environment_name(args.env_name))
    portless = PortlessConfig(namespace=project, proxy_port=1355, tld="localhost")

    frontend_url = portless.url("frontend")
    landing_url = portless.url("landing")
    replacements = {
        "COMPOSE_PROJECT_NAME": project,
        "PORTLESS_NAMESPACE": portless.namespace,
        "PORTLESS_PROXY_PORT": str(portless.proxy_port),
        "PORTLESS_TLD": portless.tld,
        "FRONTEND_HOST": portless.host("frontend"),
        "LANDING_HOST": portless.host("landing"),
        "FRONTEND_URL": frontend_url,
        "LANDING_URL": landing_url,
        "PUBLIC_BACKEND_URL": portless.url("api"),
        "PUBLIC_CHAT_URL": portless.url("chat"),
        "ALLOWED_HOSTS": f"localhost,127.0.0.1,api,{portless.host('api')}",
        "CORS_ALLOWED_ORIGINS": f"{frontend_url},{landing_url}",
        "CSRF_TRUSTED_ORIGINS": f"{frontend_url},{landing_url}",
    }

    template = (WORKSPACE_ROOT / ".env.example").read_text(encoding="utf-8")
    try:
        write_exclusive(destination, replace_values(template, replacements))
    except (FileExistsError, ValueError) as error:
        raise SystemExit(str(error)) from None

    print(f"Created {destination}")
    print(f"Compose project: {project}")
    print(f"Frontend: {frontend_url}")
    print(f"Landing:  {landing_url}")
    print(f"Backend:  {portless.url('api')}")
    print(f"Chat:     {portless.url('chat')}")


if __name__ == "__main__":
    main()
