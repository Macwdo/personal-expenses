# Pingou o que?

Umbrella workspace for the Pingou o que? product — a single-user personal
finance organizer with an AI chat assistant. This repo only groups the child
repositories as Git submodules. It has no runtime, Compose stack or Makefile:
each child owns its code, tooling, infrastructure and how it runs.

## Child Repositories

- `pingou-o-que-frontend`: authenticated Next.js product UI, including routes,
  components, table workflows, the chat UI, hooks, Zustand stores, and API
  client wrappers.
- `pingou-o-que-backend`: Django/DRF API for financial organization, backed by
  PostgreSQL. Organized around models, serializers, selectors, services,
  migrations, seed data, and tests, plus Celery workers and a
  LangGraph/DeepAgents chat agent (`apps/ai`).
- `pingou-o-que-landing-page`: public marketing site for the product, built with
  Next.js and shadcn-style components, including the CRM lead form.
- `pingou-o-que-chat`: stateless Go service that relays chat events to the
  browser as Server-Sent Events.
- `pingou-o-que-infra`: the whole stack on a local kind cluster (Kustomize
  overlay, PostgreSQL and MinIO in-cluster).
- `pingou-o-que-infra-paas`: Terraform for the PaaS production setup
  (Supabase, Railway, Vercel).

## How the pieces fit together

1. The frontend sends a chat message to the Go service, which proxies it to
   Django.
2. Django validates it and enqueues a Celery task that runs the finance agent
   and appends ordered chat events to PostgreSQL.
3. The frontend opens an SSE connection to the Go service, which verifies the
   token against Django and relays that thread's event log to the browser.

PostgreSQL is the only persistent store: domain data, LangGraph history, the
Celery broker and results, Beat schedules and chat events.

## Running

Run each project from its own repository, following its README. To run the
whole stack together, use one of the infrastructure repositories.

## Working model

Use this repository only for cross-repository notes and submodule pointer
updates. Code, tests and validation belong to the owning child repository.
Durable rules live in `AGENTS.md`.

Work directly in the primary checkout and primary branch of every repository:
`main` for the parent, backend, frontend, and landing repositories, and
`master` for the chat repository while that remains its upstream primary
branch. Do not create feature branches or Git worktrees.

After cloning, initialize submodules:

```bash
git submodule update --init --recursive
```

## Fixture-backed development data

`pingou-o-que-backend/apps/api/fixtures/financial_seed.json` is the single
source for bootstrap, demo, and local domain data, loaded by the backend's
idempotent fixture loader. Runtime-created state, such as real chat sessions,
remains runtime state.

Every backend model, relationship, business-state, or create/mutate-flow change
must update that fixture and `apps/core/tests/test_seed.py` in the same child
repository change. Keep 10-20 representative records per domain model or new
business flow; relationship-generated rows may exceed that when needed, while
fixed infrastructure identities may remain singletons. Do not introduce
bootstrap data through migrations, startup hooks, service defaults, or ad hoc
scripts.
