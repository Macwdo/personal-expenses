from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.dev.config import PortlessConfig, WORKSPACE_ROOT, read_env, resolve_env_file


@dataclass(frozen=True)
class Route:
    service: str
    container_port: int


ROUTES = {
    route.service: route
    for route in (
        Route("frontend", 3000),
        Route("landing", 3000),
        Route("api", 8000),
        Route("chat", 8080),
        Route("flower", 5555),
    )
}
DEFAULT_SERVICES = ("frontend", "landing", "api", "chat")


def require_portless() -> str:
    executable = shutil.which("portless")
    if executable is None:
        raise SystemExit(
            "portless is required; install it with: npm install -g portless"
        )
    return executable


def compose_command(env_file: Path, *arguments: str) -> list[str]:
    return [
        "docker",
        "compose",
        "--env-file",
        str(env_file),
        "--file",
        str(WORKSPACE_ROOT / "compose.yaml"),
        *arguments,
    ]


def published_port(env_file: Path, route: Route) -> int:
    result = subprocess.run(
        compose_command(env_file, "port", route.service, str(route.container_port)),
        check=True,
        capture_output=True,
        text=True,
    )
    match = re.search(r":(\d+)\s*$", result.stdout)
    if match is None:
        raise RuntimeError(
            f"could not parse published port for {route.service}: {result.stdout!r}"
        )
    return int(match.group(1))


def start_proxy(executable: str, config: PortlessConfig) -> None:
    environment = os.environ.copy()
    environment["PORTLESS_HTTPS"] = "0"
    environment["PORTLESS_PORT"] = str(config.proxy_port)
    environment["PORTLESS_TLD"] = config.tld
    subprocess.run(
        [
            executable,
            "proxy",
            "start",
            "-p",
            str(config.proxy_port),
            "--tld",
            config.tld,
        ],
        check=True,
        env=environment,
    )

    probe_name = f"probe.{config.namespace}"
    result = subprocess.run(
        [executable, "get", probe_name, "--no-worktree"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    actual_url = result.stdout.strip()
    expected_url = config.url("probe")
    if actual_url != expected_url:
        raise SystemExit(
            "the running Portless proxy does not match this environment: "
            f"expected {expected_url}, got {actual_url}. Stop the conflicting "
            "proxy with `portless proxy stop`, then run `make portless-up`."
        )


def add_routes(
    env_file: Path, config: PortlessConfig, services: tuple[str, ...]
) -> None:
    executable = require_portless()
    start_proxy(executable, config)

    for service in services:
        route = ROUTES[service]
        port = published_port(env_file, route)
        name = config.route_name(service)
        subprocess.run([executable, "alias", name, str(port), "--force"], check=True)
        print(f"{service:8} {config.url(service)} -> 127.0.0.1:{port}")


def remove_routes(config: PortlessConfig, services: tuple[str, ...]) -> None:
    executable = shutil.which("portless")
    if executable is None:
        return

    for service in services:
        subprocess.run(
            [executable, "alias", "--remove", config.route_name(service)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage Portless aliases for the Compose stack."
    )
    parser.add_argument("action", choices=("add", "remove", "show"))
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--services", nargs="+", choices=tuple(ROUTES))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env_file = resolve_env_file(args.env_file)
    try:
        config = PortlessConfig.from_env(read_env(env_file))
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from None
    services = tuple(args.services or DEFAULT_SERVICES)

    if args.action == "add":
        add_routes(env_file, config, services)
    elif args.action == "remove":
        remove_routes(config, services)
    else:
        for service in services:
            print(f"{service:8} {config.url(service)}")


if __name__ == "__main__":
    main()
