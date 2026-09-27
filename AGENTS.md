# Repository Guidelines

## Project Structure & Module Organization

This repository is a Git superproject and only a workspace: it holds no
runtime, Compose stack, Makefile or infrastructure. Its submodules are the app
repositories `pingou-o-que-backend/`, `pingou-o-que-frontend/`,
`pingou-o-que-landing-page/`, `pingou-o-que-chat/`, and the infrastructure
repositories `pingou-o-que-infra/` (Kubernetes) and `pingou-o-que-infra-paas/`
(Terraform). Never add runtime or infrastructure files to the root; they
belong in the owning child repository. Run
`git submodule update --init --recursive` after cloning or when pointers change.
Backend Django settings live in `pingou-o-que-backend/config/`; domain code
lives in `pingou-o-que-backend/apps/<app>/`; backend tests live beside each app
in `apps/<app>/tests/`. The frontend and landing apps are Next.js projects with
routes in `app/`, shared UI in `components/`, hooks in `hooks/`, API/client
utilities in `lib/`, Zustand stores in `stores/`, and static assets in
`public/`. `pingou-o-que-chat` is a small Go HTTP service (`main.go` +
`internal/*`).

## Child Repository Roles

- `pingou-o-que-frontend`: authenticated Next.js product UI. It owns product
  routes, React components, table workflows, the chat UI, API client wrappers
  (`lib/api/*`), hooks, and Zustand stores.
- `pingou-o-que-backend`: Django/DRF API backed by PostgreSQL, with Celery
  workers and a LangGraph/DeepAgents chat agent. It owns models, serializers,
  selectors, services, migrations, fixture-backed seed data, and API tests.
- `pingou-o-que-landing-page`: public marketing site. It owns public pages,
  marketing copy, visual sections, the CRM lead form, and shadcn-style UI.
- `pingou-o-que-chat`: stateless Go service that relays chat events to browsers.
  It proxies chat-start to Django, verifies tokens against Django, and streams a
  thread's PostgreSQL event log to the client as Server-Sent Events.
- `pingou-o-que-infra`: the whole stack on a local kind cluster (Kustomize
  overlay, PostgreSQL and MinIO in-cluster, driven by its Makefile).
- `pingou-o-que-infra-paas`: Terraform for production on Supabase, Railway and
  Vercel.

## Runtime Architecture

The frontend sends chat-start/approval requests to the stateless Go relay.
Django owns validation, authentication, session ownership, business rules and
dispatch. Celery uses PostgreSQL through Kombu SQLAlchemy as broker and its
SQLAlchemy database result backend. One Celery Beat uses django-celery-beat
DatabaseScheduler in PostgreSQL and also performs queue/result/event cleanup.

Tasks append ordered PostgreSQL chat event rows. Go forwards the bearer token
to Django's bounded event endpoint and polls for SSE delivery, supporting numeric
Last-Event-ID cursors. PostgreSQL also owns domain data and LangGraph history.
No Redis, SQS or Supabase Realtime is required.

Private documents use S3-compatible storage through boto3 presigned PUT/GET
URLs. Django talks to storage at `S3_ENDPOINT_URL` and signs browser URLs for
`S3_PUBLIC_ENDPOINT_URL`, since a presigned URL is bound to its host.

Deployment is owned by the infrastructure repositories. Supabase Auth integration
is still pending; current authentication retains the DEBUG dev-token path.
Keep production readiness false until Auth and single-user access checks pass.
Backend AGENTS.md documents SQL broker delivery limitations.

## Branch And Ownership

Work directly in each repository's primary checkout and primary branch. The
durable rules are:

- Use the parent repo for cross-repo product notes and commits that update child
  submodule pointers.
- Implement app code in the owning child repository's primary checkout, never
  in the parent repository.
- Branch ownership and validation commands follow the repo that owns the change.
  A session may start in one child repo and still inspect siblings for context
  (e.g. checking backend routes when changing the frontend client).
- Work on `main` in the parent, backend, frontend, and landing repositories.
  The chat repository currently uses `master` as its upstream primary branch;
  use it directly until that upstream branch is intentionally renamed.
- Do not create feature branches or Git worktrees. Work sequentially in the
  primary checkout, one change at a time, unless the user explicitly asks for
  parallel work.
- Do not create OpenSpec artifacts or repository spec trees. Keep durable rules
  in `AGENTS.md`.
- Validate and commit in each owning child repository before intentionally
  updating its parent submodule pointer.

## Coding Style & Naming Conventions

Backend Python targets 3.13 and uses Ruff: space indentation, double quotes, and a 131-character line length. Keep Django boundaries clear: selectors handle reads, services handle writes/business rules, serializers handle validation and representation, and views stay thin. Use snake_case for Python modules/functions.

The Go service uses standard `gofmt`/`go vet`; keep the event-page contract in `internal/dbstream` aligned with Django's chat events endpoint.

In Next.js apps, use TypeScript, ESLint, Prettier, Tailwind, and shadcn/ui patterns. Component names are PascalCase; route and component files commonly use kebab-case. The frontend runs Next 16.2 / React 19.2 with breaking changes from older Next.js conventions — check `node_modules/next/dist/docs/` before assuming familiar APIs. Frontend HTTP calls must go through `lib/api/*` (`requestApi`/`requestApiVoid` plus Zod schemas), never directly from components; the backend base URL comes from `NEXT_PUBLIC_EXPENSE_API_URL` (local default `http://127.0.0.1:8067`) and the chat service URL from `NEXT_PUBLIC_CHAT_API_URL`. Neither app exposes or consumes `/table` endpoints — data-grid screens use the standard list routes with pagination/filtering/`ordering`.

Simple frontend list screens and their loading states must use
`ListPageShell`. The shell owns a fixed height equal to the viewport remaining
below the application header. Infinite-list screens use `scrollMode="list"` so
the page-level overflow stays hidden and `InfiniteList.Viewport` is the only
vertical scroll container; its scrollbar stays visually hidden. Do not
duplicate the shell's `<main>` spacing or replace its fixed height with
content-driven `min-height` in individual routes.

## AI Tool & Domain-App Boundaries

The backend `apps/ai` app owns chat orchestration (LangGraph/DeepAgents: a
`finance-router` that delegates to an `expenses-agent` and a
`transactions-agent`) but owns none of the domain logic. Every domain app that
exposes AI tools (`expenses`, `payments`, `transactions`, and any future one)
must expose a clean, DTO-based boundary that `apps/ai` builds on:

- **`dtos.py`** — one Pydantic DTO per entity the app returns to callers
  outside itself (e.g. `TransactionDTO`, `ExpenseDTO`, `PaymentDTO`,
  `InstallmentDTO`), each with a `from_model()` classmethod. Any operation
  taking more than ~4 parameters must take a single input DTO named
  `<Entity>CreateInput`, `<Entity>UpdateInput`, or `<Entity>ListFilters`.
  Every DTO extends `apps.core.dtos.BaseDTO` (or its `CamelCaseDTO` /
  `PascalCaseDTO` variants) — never `@dataclass` or a bare `BaseModel`. See
  the backend `AGENTS.md` "DTOs" section for the rules.
- **`services.py`** (writes/business rules) and/or **`selectors.py`** (reads) —
  every entity queried across apps needs a `list_<entity>` function plus `get_`,
  `create_`/`add_`, `update_`, and `delete_` counterparts as needed. These
  return DTOs (or lists of DTOs), never raw querysets, to callers outside their
  own app.
- **`agent_tools.py`** — the only module `apps/ai` imports from. Tool functions
  may import their **own** app's `enums`, `dtos`, and `services`/`selectors`, and
  **DTOs** from other apps. They must **never import models, querysets, `Q`
  objects, or serializers** — from any app. Convert any borrowed model instance
  to a DTO immediately.

When adding a new AI-exposed capability: add/extend the DTO(s) → add the
service/selector function(s) that return DTOs → add the `agent_tools.py`
function(s) → register them in `apps/ai/tool_registry.py` → attach them to the
right subagent's tool list in `apps/ai/subagents.py`.

## Testing Guidelines

Backend tests use pytest, pytest-django, DRF `APIClient`, and PostgreSQL. Prefer shared helpers in `apps/api/tests/` and place new coverage in the owning app's `tests/` package. Name tests descriptively with `test_...`. The Go service is tested with `go test ./...`. No frontend test runner is currently configured; validate UI changes with lint, typecheck, build, and screenshots when behavior or layout changes.

All bootstrap, demo, and local domain data must come from
`pingou-o-que-backend/apps/api/fixtures/financial_seed.json`. Every backend
model, relationship, business-state, or create/mutate-flow change must update
that fixture and `apps/core/tests/test_seed.py` in the same change, with 10-20
representative records per domain model or new business flow. Fixed
infrastructure identities may remain singletons. Do not add bootstrap records
via migrations, startup hooks, service defaults, or ad hoc scripts.

## Commit & Pull Request Guidelines

Root history mainly uses concise imperative commits such as `chore: update app submodules`. Prefer Conventional-style prefixes (`chore:`, `fix:`, `feat:`) when helpful. PRs should summarize changed behavior, list validation commands, call out migrations or environment changes, link issues, and include screenshots for visible UI changes.

## Security & Configuration Tips

Do not commit secrets or local `.env*` files; each child repository owns its own environment files. PostgreSQL supplies Celery broker/results and chat streaming. Keep submodule pointer updates intentional and mention them in PRs.
