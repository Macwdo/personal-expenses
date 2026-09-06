---
name: pingou-env
description: Runs every Pingou workspace runtime operation through the root Makefile - creating the local .env, building and starting the primary-checkout stack, printing Portless URLs, following logs, seeding fixture data, running Django management commands, opening psql or redis-cli, and stopping or destroying the environment. Use whenever the user asks to create the env, subir/derrubar o projeto, rodar o stack, ver URLs ou logs, resetar dados locais, or operate the environment in /home/macwdo/Codes/pingou-o-que.
---

# Pingou Environment

This skill is the **only** approved way to operate the Pingou runtime. Follow it
literally; do not improvise equivalent Docker or shell commands.

## Use this skill when

Invoke it immediately, without asking permission, for any of these requests:

| Request | Entry point below |
| --- | --- |
| "cria um env", "create the environment", `.env` is missing | [1. Create](#1-create-the-environment-file) |
| "sobe o projeto", "start everything", "run the stack" | [2. Start](#2-start-the-stack) |
| "qual a URL", "abre o front", "cadê o backend" | [3. Inspect](#3-inspect-a-running-environment) |
| "vê os logs", "o Celery quebrou", "está de pé?" | [3. Inspect](#3-inspect-a-running-environment) |
| "reseta os dados", "roda o seed", "roda uma migration" | [4. Operate backend data](#4-operate-backend-data) |
| "derruba", "para tudo", "apaga esse ambiente" | [5. Stop or delete](#5-stop-or-delete) |

## Do not use this skill for

- Editing application code — that belongs to the owning child repository.

## Invariants

These hold for every step. Violating one is a defect.

1. Run every command from the workspace root
   (`/home/macwdo/Codes/pingou-o-que`), never from a child repository.
2. Use the root `Makefile` targets only. Never call `docker compose`, `docker`,
   `psql`, or `portless` directly. If a reusable operation is missing, add a Make
   target instead of a one-off command.
3. `.env` is the supported default and must select the four primary child
   checkouts. Do not create a feature environment unless the user explicitly
   requests one.
4. Never print, paste, echo, diff, or commit the contents of `.env` or another
   local environment file. They hold real API keys.
5. Never allocate or hardcode host ports. Docker picks them; Portless names them.
6. `make up`, `make dev`, and `make seed` **reset fixture-owned domain data**.
   Ask the user first when runtime-created local data might matter.
7. `make destroy` deletes volumes and images. Ask the user first, always.

## 1. Create the environment file

Check first, because `env-init` refuses to overwrite:

```bash
ls -la .env 2>/dev/null
```

If the file already exists, skip to step 2. Otherwise create it:

```bash
make env-init ENV_NAME=main
```

The target prints the Compose project name and the four Portless URLs. It
derives a unique namespace from `ENV_NAME` plus a checksum of the workspace
path, so two environments never collide.

Then tell the user to set, in the generated file, the API key matching
`AI_CHAT_MODEL` (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`), which is required
before the chat works. The four `*_PATH` values already select the primary child
checkouts; do not redirect them to alternate checkouts.

Change nothing else in the generated file.

## 2. Start the stack

```bash
make doctor
make up
make urls
```

Use `make config` first when the environment file was edited by hand and the
rendered Compose output needs review.

`make up` builds the four application images, starts PostgreSQL, Redis, Django,
the Celery worker, the Go relay, the frontend, and the landing page, waits for
health checks, loads the backend fixture, and registers Portless aliases. It is
slow on a cold build; allow several minutes rather than interrupting it.

Use `make dev ENV_FILE=<selected-env>` instead when the user wants Compose Watch
to keep running and sync source changes.

Report the URLs printed by `make urls`. Never construct a URL by hand.

Failure handling:

- `make doctor` fails → Docker or Portless is unavailable. Report it and stop.
- A service never becomes healthy → run
  `make logs SERVICE=<service>`, report the real error,
  and do not retry blindly.
- Public URLs look stale in the browser → Next.js reads them at process start,
  so run `make up` again after any environment-file change.

## 3. Inspect a running environment

```bash
make ps
make urls
make logs SERVICE=<service>
make restart SERVICE=<service>
```

Service names are `api`, `celery-worker`, `chat`, `frontend`, `landing`, `db`,
and `redis`. `make logs` follows output, so run it in the background or bound it
when a single snapshot is enough.

Optional profiles: `make scheduler` (Celery Beat) and `make flower` (Flower,
which also registers its own Portless alias).

## 4. Operate backend data

```bash
make seed
make migrate
make manage ARGS="<django-command>"
make db-shell
make redis-cli
```

All local domain data comes from
`pingou-o-que-backend/apps/api/fixtures/financial_seed.json`. To change seeded
data, edit that fixture in the backend repository and re-run `make seed` — never
insert rows through `db-shell`, a migration, or an ad hoc script.

### Backend running locally in its virtual environment

When the traceback comes from the backend `.venv` and the root Compose stack
is stopped, use the root targets below. They use the backend's own `.env`,
not the root Compose `ENV_FILE`. `LOCAL_BACKEND_PATH` defaults to the primary
backend checkout.

```bash
make local-manage ARGS="showmigrations"
make local-reset-db CONFIRM_RESET=1
```

`local-reset-db` is destructive: obtain user authorization first. It requires
DEBUG and a loopback PostgreSQL host, clears the configured database's public
schema, regenerates app migrations from current models, applies migrations,
and loads `financial_seed.json`. This follows the backend's disposable database
policy. Validate the seed tests and affected API after reset. Never use it on
a shared or production database.

## 5. Stop or delete

```bash
make stop     # pause containers, keep everything
make down     # remove containers + aliases, keep volumes
make destroy  # also delete volumes and local images
```

Default to `make down`. Use `make destroy` only after the user explicitly agrees
to lose that environment's database.

## Report back

Close every run with: the environment file used, the Portless URLs, the state
from `make ps`, whether fixture data was reset, and any command that failed with
its real error output.
