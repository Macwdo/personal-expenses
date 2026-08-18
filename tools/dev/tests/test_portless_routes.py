from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.dev.portless_routes import Route, published_port


class PublishedPortTests(unittest.TestCase):
    @patch("tools.dev.portless_routes.subprocess.run")
    def test_published_port_parses_ipv4_binding(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="127.0.0.1:49152\n", stderr=""
        )

        self.assertEqual(published_port(Path("/tmp/.env"), Route("api", 8000)), 49152)

    @patch("tools.dev.portless_routes.subprocess.run")
    def test_published_port_rejects_unexpected_output(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not-a-port\n", stderr=""
        )

        with self.assertRaisesRegex(RuntimeError, "could not parse"):
            published_port(Path("/tmp/.env"), Route("api", 8000))


if __name__ == "__main__":
    unittest.main()
