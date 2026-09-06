"""Rebuild the disposable local backend database, migrations, and fixture data."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import django
from django.conf import settings
from django.core.management import call_command
from django.db import connection


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", action="store_true", help="Confirm clearing the local backend public schema.")
    args = parser.parse_args()
    if not args.confirm:
        parser.error("Database reset requires CONFIRM_RESET=1 after user approval.")

    backend = Path.cwd()
    sys.path.insert(0, str(backend))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    database = connection.settings_dict
    if not settings.DEBUG or database["HOST"] not in {"localhost", "127.0.0.1", "::1"}:
        raise SystemExit("Reset requires DEBUG and a loopback database host.")
    if connection.vendor != "postgresql" or database["NAME"] in {"template0", "template1"}:
        raise SystemExit("Reset requires a PostgreSQL application database.")

    from django.db import transaction

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE")
        cursor.execute("CREATE SCHEMA public")
    connection.close()

    for migration in sorted((backend / "apps").glob("*/migrations/*.py")):
        if migration.name != "__init__.py":
            migration.unlink()
    call_command("makemigrations", interactive=False)
    call_command("migrate", interactive=False)

    from scripts import seed

    seed.main()
    call_command("makemigrations", check=True, dry_run=True, interactive=False)
    print("Local public schema rebuilt; migrations applied and fixtures loaded.")


if __name__ == "__main__":
    main()
