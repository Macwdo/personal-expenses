# Repository Guidelines

## Project Structure & Module Organization

This repository is a Git superproject with four app submodules:
`pingou-o-que-backend/`, `pingou-o-que-frontend/`,
`pingou-o-que-landing-page/`, and `pingou-o-que-chat/`. Run
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
  selectors, services, migrations, seed data, API tests, and the backend
  `openspec/` artifacts (the only repo that still keeps OpenSpec).
- `pingou-o-que-landing-page`: public marketing site. It owns public pages,
  marketing copy, visual sections, the CRM lead form, and shadcn-style UI.
- `pingou-o-que-chat`: stateless Go service that relays chat events to browsers.
  It proxies chat-start to Django, verifies tokens against Django, and streams a
  thread's Redis Stream to the client as Server-Sent Events.

## Runtime Architecture

The product is a single-user personal finance app. The four services cooperate
at runtime:

1. Browser (frontend) sends a chat message to the **Go chat service**
   (`POST /chat`), which proxies it to Django's internal chat-start endpoint.
2. **Django** validates the request, records the session, and enqueues a
   **Celery** task. The task runs the LangGraph/DeepAgents finance agent
   (`apps/ai`) and publishes streaming events (`token`/`agent`/`complete`/
   `error`) to a per-thread **Redis Stream** (`chat:stream:<thread_id>`), with
   thread ownership stored at `chat:owner:<thread_id>`.
3. The browser opens `GET /chat/{thread_id}/events` on the **Go service**, which
   verifies the bearer token via Django (`/internal/auth/verify`), checks Redis
   thread ownership, and relays the Redis Stream to the browser as SSE.

Redis is the broker/result backend for Celery **and** the chat event bus.
PostgreSQL is the only persistent datastore (including the LangGraph
checkpointer that holds conversation history). There is no real auth yet: the
only token path is a `DEBUG`-only dev-token endpoint.

## Worktree And Ownership

- Use the parent repo for cross-repo product notes and commits that update child
  submodule pointers.
- Do not implement app code from a parent-repo worktree.
- Branch ownership and validation commands follow the repo that owns the change.
  A session may start in one child repo and still inspect siblings for context
  (e.g. checking backend routes when changing the frontend client).
- OpenSpec artifacts now live only in `pingou-o-que-backend/openspec`; the root,
  frontend, and landing-page no longer carry an `openspec/` tree.

## Mires AIW Usage

- For app-only work, run `mires-aiw create <branch-name>` inside the child repo
  that owns the change.
- For multi-app work, run
  `mires-aiw workspace list --folder /home/macwdo/Codes/pingou-o-que` first,
  then create worktrees for explicit child repo names.
- Use `--all` only when the requested change truly touches every direct child
  Git repo in this workspace.
- Use parent-repo `mires-aiw create` only for parent-owned work such as
  submodule pointer updates or workspace documentation.

## Build, Test, and Development Commands

- `cd pingou-o-que-backend && make up`: start PostgreSQL, run migrations, and serve Django on `8001`.
- `cd pingou-o-que-backend && make celery-worker`: run the Celery worker (needed for chat replies).
- `cd pingou-o-que-backend && uv run pytest`: run backend tests.
- `cd pingou-o-que-backend && uv run ruff check . && uv run ruff format .`: lint and format Python.
- `cd pingou-o-que-chat && go run .`: start the Go chat SSE relay on `8080`.
- `cd pingou-o-que-chat && go build ./... && go test ./...`: build and test the Go service.
- `cd pingou-o-que-frontend && bun run dev`: run the product UI locally.
- `cd pingou-o-que-landing-page && bun run dev`: run the marketing site locally.
- `bun run build`, `bun run lint`, and `bun run typecheck`: validate either Next.js app from its directory.

## Coding Style & Naming Conventions

Backend Python targets 3.13 and uses Ruff: space indentation, double quotes, and a 131-character line length. Keep Django boundaries clear: selectors handle reads, services handle writes/business rules, serializers handle validation and representation, and views stay thin. Use snake_case for Python modules/functions.

The Go service uses standard `gofmt`/`go vet`; keep the Redis key layout in
`internal/redisstream` mirrored with Django's `apps/chat/redis.py`.

In Next.js apps, use TypeScript, ESLint, Prettier, Tailwind, and shadcn/ui patterns. Component names are PascalCase; route and component files commonly use kebab-case. The frontend runs Next 16.2 / React 19.2 with breaking changes from older Next.js conventions — check `node_modules/next/dist/docs/` before assuming familiar APIs. Frontend HTTP calls must go through `lib/api/*` (`requestApi`/`requestApiVoid` plus Zod schemas), never directly from components; the backend base URL comes from `NEXT_PUBLIC_EXPENSE_API_URL` (local default `http://127.0.0.1:8001`) and the chat service URL from `NEXT_PUBLIC_CHAT_API_URL`. Neither app exposes or consumes `/table` endpoints — data-grid screens use the standard list routes with pagination/filtering/`ordering`.

## AI Tool & Domain-App Boundaries

The backend `apps/ai` app owns chat orchestration (LangGraph/DeepAgents: a
`finance-router` that delegates to an `expenses-agent` and a
`transactions-agent`) but owns none of the domain logic. Every domain app that
exposes AI tools (`expenses`, `payments`, `transactions`, and any future one)
must expose a clean, DTO-based boundary that `apps/ai` builds on:

- **`dtos.py`** — one frozen `@dataclass` per entity the app returns to callers
  outside itself (e.g. `TransactionDTO`, `ExpenseDTO`, `PaymentDTO`,
  `InstallmentDTO`), each with a `from_model()` classmethod. Any operation
  taking more than ~4 parameters must take a single input dataclass named
  `<Entity>CreateInput`, `<Entity>UpdateInput`, or `<Entity>ListFilters`.
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

## Commit & Pull Request Guidelines

Root history mainly uses concise imperative commits such as `chore: update app submodules`. Prefer Conventional-style prefixes (`chore:`, `fix:`, `feat:`) when helpful. PRs should summarize changed behavior, list validation commands, call out migrations or environment changes, link issues, and include screenshots for visible UI changes.

## Security & Configuration Tips

Do not commit secrets or local `.env*` files. Backend runtime settings use `.env`; Docker Compose may use `.env.development`. Redis (`REDIS_URL`) is required for Celery and chat streaming. Keep submodule pointer updates intentional and mention them in PRs.
