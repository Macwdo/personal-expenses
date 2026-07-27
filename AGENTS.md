# Repository Guidelines

## Project Structure & Module Organization

This repository is a Git superproject with three app submodules:
`pingou-o-que-backend/`, `pingou-o-que-frontend/`, and
`pingou-o-que-landing-page/`. Use `git submodule update --init --recursive`
after cloning or when pointers change. Backend Django settings live in
`pingou-o-que-backend/config/`; domain code lives in
`pingou-o-que-backend/apps/<app>/`; backend tests live beside each app in
`apps/<app>/tests/`. The frontend and landing apps are Next.js projects with
routes in `app/`, shared UI in `components/`, hooks in `hooks/`, API/client
utilities in `lib/`, and static assets in `public/`. Root OpenSpec artifacts
under `openspec/` are only for cross-repo or product-level coordination.

## Child Repository Roles

- `pingou-o-que-frontend`: authenticated Next.js product UI. It owns product
  routes, React components, table workflows, API client wrappers, hooks, and
  frontend OpenSpec artifacts.
- `pingou-o-que-backend`: Django/DRF API backed by PostgreSQL. It owns models,
  serializers, selectors, services, views, migrations, seed data, API tests, and
  backend OpenSpec artifacts.
- `pingou-o-que-landing-page`: public marketing site. It owns public pages,
  marketing copy, visual sections, shadcn-style UI composition, and
  landing-page OpenSpec artifacts.

## Worktree And Spec Ownership

- Use the parent repo for cross-repo product notes, root OpenSpec coordination,
  and commits that update child submodule pointers.
- Do not implement app code from a parent-repo worktree.
- Do not place app-only OpenSpec changes in the parent `openspec/` tree.
- Keep app-only OpenSpec changes in the owning child repo:
  - frontend changes in `pingou-o-que-frontend/openspec`
  - backend changes in `pingou-o-que-backend/openspec`
  - landing-page changes in `pingou-o-que-landing-page/openspec`
- A Codex session may start in a child repo and still inspect sibling repos for
  context, but branch ownership, OpenSpec ownership, and validation commands
  must follow the repo that owns the change.

## Mires AIW Usage

- For app-only work, run `mires-aiw create <branch-name>` inside the child repo
  that owns the change.
- For multi-app work, run
  `mires-aiw workspace list --folder /home/macwdo/Codes/pingou-o-que` first,
  then create worktrees for explicit child repo names.
- Use `--all` only when the requested change truly touches every direct child
  Git repo in this workspace.
- Use parent-repo `mires-aiw create` only for parent-owned work such as
  submodule pointer updates, workspace documentation, or cross-repo OpenSpec
  coordination.

## Build, Test, and Development Commands

- `cd pingou-o-que-backend && make up`: start PostgreSQL, run migrations, and serve Django on `8001`.
- `cd pingou-o-que-backend && ./.venv/bin/python -m pytest`: run backend tests.
- `cd pingou-o-que-backend && ruff check . && ruff format .`: lint and format Python.
- `cd pingou-o-que-frontend && bun run dev`: run the product UI locally.
- `cd pingou-o-que-landing-page && bun run dev`: run the marketing site locally.
- `bun run build`, `bun run lint`, and `bun run typecheck`: validate either Next.js app from its directory.

## Coding Style & Naming Conventions

Backend Python targets 3.13 and uses Ruff: space indentation, double quotes, and a 131-character line length. Keep Django boundaries clear: selectors handle reads, services handle writes/business rules, serializers handle validation and representation, and views stay thin. Use snake_case for Python modules/functions. Backend models in `categories`, `expenses`, `payments`, and `chat` are consolidated under `app_label = "api"`, so their migrations live in `apps/api/migrations/`, not their own app's `migrations/` dir.

In Next.js apps, use TypeScript, ESLint, Prettier, Tailwind, and shadcn/ui patterns. Component names are PascalCase; route and component files commonly use kebab-case. The frontend runs Next 16.2 / React 19.2 with breaking changes from older Next.js conventions — check `node_modules/next/dist/docs/` before assuming familiar APIs. Frontend HTTP calls must go through `lib/api/*` (`requestApi`/`requestApiVoid` plus Zod schemas), never directly from components; the backend base URL comes from `NEXT_PUBLIC_EXPENSE_API_URL` (local default `http://127.0.0.1:8001`). Neither app exposes or consumes `/table` endpoints — data-grid screens use the standard list routes with pagination/filtering/`ordering`.

## AI Tool & Domain-App Boundaries

The backend `apps/ai` app exposes DeepAgents tools for the chat agent, but it owns none of the domain logic. Every
domain app (`transactions`, `expenses`, `payments`, and any future app that gets AI tools) must expose a clean,
DTO-based boundary that `apps/ai` builds on:

- **`dtos.py`** — one frozen `@dataclass` per entity the app returns to callers outside itself (e.g. `TransactionDTO`,
  `ExpenseDTO`, `PaymentDTO`, `InstallmentDTO`), each with a `from_model()` classmethod that converts a model instance.
  Any function taking more than ~4 parameters (especially create/update/list operations) must take a single input
  dataclass instead of a long parameter list, named `<Entity>CreateInput`, `<Entity>UpdateInput`, or
  `<Entity>ListFilters`.
- **`services.py`** (write/business-rule operations) and/or **`selectors.py`** (read/aggregation queries) — every
  entity that is queried across apps needs a `list_<entity>` function here (e.g. `list_transactions`,
  `list_expenses`, `list_payments`, `list_installments`) plus `get_`, `create_`/`add_`, `update_`, and `delete_`
  counterparts as needed. These functions return DTOs (or lists of DTOs), never raw querysets, to any caller outside
  their own app.
- **`agent_tools.py`** — the only module `apps/ai` imports from. Tool functions here may import their **own** app's
  `enums`, `dtos`, and `services`/`selectors` functions, and **DTOs** from other apps (e.g. `apps.expenses.dtos`,
  `apps.payments.dtos`). They must **never import models, querysets, `Q` objects, or serializers** — from their own
  app or any other. If a service function briefly returns another app's model instance (e.g. a link/reconciliation
  call), convert it to that app's DTO immediately and do not hold onto or return the model itself.

When adding a new AI-exposed capability, follow this order: add/extend the DTO(s) in `dtos.py` → add the
service/selector function(s) that return DTOs → add the `agent_tools.py` function(s) that call them → register the
new functions in `apps/ai/tool_registry.py` → attach them to the right subagent's tool list in `apps/ai/subagents.py`.

## Testing Guidelines

Backend tests use pytest, pytest-django, DRF `APIClient`, and PostgreSQL. Prefer shared helpers in `apps/api/tests/` and place new coverage in the owning app’s `tests/` package. Name tests descriptively with `test_...`. No frontend test runner is currently configured; validate UI changes with lint, typecheck, build, and screenshots when behavior or layout changes.

## Commit & Pull Request Guidelines

Root history mainly uses concise imperative commits such as `chore: update app submodules`. Prefer Conventional-style prefixes (`chore:`, `fix:`, `feat:`) when helpful. PRs should summarize changed behavior, list validation commands, call out migrations or environment changes, link issues, and include screenshots for visible UI changes.

## Security & Configuration Tips

Do not commit secrets or local `.env*` files. Backend runtime settings use `.env`; Docker Compose may use `.env.development`. Keep submodule pointer updates intentional and mention them in PRs.
