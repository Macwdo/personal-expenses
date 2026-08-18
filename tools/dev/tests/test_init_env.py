from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from tools.dev.init_env import project_name, replace_values, slugify, write_exclusive


class InitEnvTests(unittest.TestCase):
    def test_slugify_normalizes_and_bounds_names(self) -> None:
        self.assertEqual(slugify("Fix/Auth_and Chat"), "fix-auth-and-chat")
        self.assertLessEqual(len(slugify("x" * 100)), 32)

    def test_project_name_is_stable_and_namespaced(self) -> None:
        self.assertEqual(project_name("Feature One"), project_name("Feature One"))
        self.assertTrue(project_name("Feature One").startswith("pingou-feature-one-"))

    def test_replace_values_requires_every_contract_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "MISSING"):
            replace_values("KNOWN=value\n", {"MISSING": "replacement"})

    def test_write_exclusive_creates_private_file_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / ".env"
            write_exclusive(destination, "TOKEN=placeholder\n")

            self.assertEqual(destination.read_text(encoding="utf-8"), "TOKEN=placeholder\n")
            self.assertEqual(os.stat(destination).st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                write_exclusive(destination, "TOKEN=other\n")


if __name__ == "__main__":
    unittest.main()
