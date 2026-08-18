from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.dev.config import PortlessConfig, read_env


class ReadEnvTests(unittest.TestCase):
    def test_read_env_ignores_comments_and_unquotes_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "# local values\nPLAIN=value\nDOUBLE=\"two words\"\nSINGLE='three'\n",
                encoding="utf-8",
            )

            self.assertEqual(
                read_env(env_file),
                {"PLAIN": "value", "DOUBLE": "two words", "SINGLE": "three"},
            )


class PortlessConfigTests(unittest.TestCase):
    def test_from_env_builds_namespaced_urls(self) -> None:
        config = PortlessConfig.from_env(
            {
                "PORTLESS_NAMESPACE": "pingou-feature",
                "PORTLESS_PROXY_PORT": "1355",
                "PORTLESS_TLD": "localhost",
            }
        )

        self.assertEqual(config.route_name("api"), "api.pingou-feature")
        self.assertEqual(
            config.url("api"), "http://api.pingou-feature.localhost:1355"
        )

    def test_from_env_rejects_missing_namespace(self) -> None:
        with self.assertRaisesRegex(ValueError, "PORTLESS_NAMESPACE is required"):
            PortlessConfig.from_env({})

    def test_from_env_rejects_invalid_proxy_port(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be between"):
            PortlessConfig.from_env(
                {"PORTLESS_NAMESPACE": "pingou", "PORTLESS_PROXY_PORT": "70000"}
            )


if __name__ == "__main__":
    unittest.main()
