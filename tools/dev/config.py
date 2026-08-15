from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def resolve_env_file(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = WORKSPACE_ROOT / path
    return path.resolve()


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


@dataclass(frozen=True)
class PortlessConfig:
    namespace: str
    proxy_port: int
    tld: str

    @classmethod
    def from_env(cls, values: dict[str, str]) -> PortlessConfig:
        namespace = values.get("PORTLESS_NAMESPACE", "").strip()
        if not namespace:
            raise ValueError("PORTLESS_NAMESPACE is required")

        proxy_port = int(values.get("PORTLESS_PROXY_PORT", "1355"))
        if not 1 <= proxy_port <= 65535:
            raise ValueError("PORTLESS_PROXY_PORT must be between 1 and 65535")

        tld = values.get("PORTLESS_TLD", "localhost").strip()
        if not tld:
            raise ValueError("PORTLESS_TLD is required")

        return cls(namespace=namespace, proxy_port=proxy_port, tld=tld)

    def route_name(self, service: str) -> str:
        return f"{service}.{self.namespace}"

    def host(self, service: str) -> str:
        return f"{self.route_name(service)}.{self.tld}"

    def url(self, service: str) -> str:
        return f"http://{self.host(service)}:{self.proxy_port}"
