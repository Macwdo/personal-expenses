# Pingou o que?

Umbrella workspace for the Pingou o que? product — a single-user personal
finance organizer with an AI chat assistant. This repo coordinates the child app
repositories through Git submodules; implementation code lives in the children.

## Child Repositories

- `pingou-o-que-frontend`: authenticated Next.js product UI, including routes,
  components, table workflows, the chat UI, hooks, Zustand stores, and API
  client wrappers.
- `pingou-o-que-backend`: Django/DRF API for financial organization, backed by
  PostgreSQL and Redis. Organized around models, serializers, selectors,
  services, migrations, seed data, and tests, plus Celery workers and a
  LangGraph/DeepAgents chat agent (`apps/ai`).
- `pingou-o-que-landing-page`: public marketing site for the product, built with
  Next.js and shadcn-style components, including the CRM lead form.
- `pingou-o-que-chat`: stateless Go service that relays chat events to the
  browser as Server-Sent Events, backed by Redis Streams.

## How the pieces fit together

1. The frontend sends a chat message to the Go service, which proxies it to
   Django.
2. Django validates it and enqueues a Celery task that runs the finance agent
   and publishes streaming events to a per-thread Redis Stream.
3. The frontend opens an SSE connection to the Go service, which verifies the
   token against Django and relays that Redis Stream to the browser.

PostgreSQL is the only persistent store (including the agent's conversation
history); Redis is both the Celery broker/result backend and the chat event bus.

## Working Model

Use the parent repository for cross-repo planning and submodule pointer updates.
Use the child repositories for app implementation, tests, and validation. The
backend is the only child that still keeps `openspec/` artifacts.

After cloning, initialize submodules:

```bash
git submodule update --init --recursive
```

For app-only work:

```bash
cd /home/macwdo/Codes/pingou-o-que/pingou-o-que-frontend
mires-aiw create change/example
```

For multi-app work:

```bash
cd /home/macwdo/Codes/pingou-o-que
mires-aiw workspace list --folder .
mires-aiw workspace create change/example --folder . pingou-o-que-frontend pingou-o-que-backend
```
