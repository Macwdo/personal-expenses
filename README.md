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

## Integrated development stack

The root [`compose.yaml`](./compose.yaml) starts the complete development path:

- PostgreSQL/pgvector and Redis;
- the Django API (whose entrypoint applies migrations once) and the Celery
  worker required by chat;
- the Go chat/SSE relay;
- the authenticated frontend and public landing page.

Celery Beat and Flower are available as optional profiles. Every application
uses a real Dockerfile in its owning child repository; the Compose file does
not contain inline Dockerfiles or a one-shot migration service. There are no
fixed `container_name` values: Compose namespaces containers, the default
network, and named volumes with `COMPOSE_PROJECT_NAME`.

[Portless](https://github.com/vercel-labs/portless) routes Docker's ephemeral
loopback ports to stable names. Install it once if it is not already available:

```bash
npm install -g portless
```

Create the local environment once, add the API key required by
`AI_CHAT_MODEL`, and start everything:

```bash
make env-init ENV_NAME=main
$EDITOR .env
make up
```

`make up` builds the four application images, starts the stack, resets local
domain data from the backend's versioned Django fixture, discovers the random
host ports selected by Docker, and registers Portless aliases. Run
`make urls` to print this environment's URLs. With the example namespace they
have this shape:

```text
http://frontend.pingou-<environment>-<checksum>.localhost:1355
http://landing.pingou-<environment>-<checksum>.localhost:1355
http://api.pingou-<environment>-<checksum>.localhost:1355
http://chat.pingou-<environment>-<checksum>.localhost:1355
```

PostgreSQL and Redis remain reachable only on the project-scoped Docker
network; use `make db-shell` or `make redis-cli` for direct access. The
generated `.env` is ignored by Git, and `make env-init` refuses to overwrite an
existing one.

Useful commands:

```bash
make dev                         # start everything, register aliases, then watch Go changes
make logs SERVICE=celery-worker  # follow one service
make ps                          # inspect this environment only
make urls                        # print stable Portless URLs
make doctor                      # check Docker and Portless
make seed                        # reset this environment from the backend fixture
make manage ARGS="createsuperuser"
make db-shell                    # psql inside this environment
make redis-cli                   # redis-cli inside this environment
make scheduler                   # optional Celery Beat profile
make flower                      # optional Flower profile
make down                        # remove containers/aliases, preserve named volumes
make destroy                     # delete this environment's containers, volumes, and images
```

`make down` preserves PostgreSQL, Redis, images, and Next.js build caches.
`make destroy` intentionally deletes the selected environment's named volumes
and locally built images. Use the Make targets as the supported interface:
they also serialize the two Bun image builds and keep Portless aliases
synchronized.

## Working model

Use the parent repository for cross-repository infrastructure, runtime
coordination, and submodule pointer updates. Use each child repository for its
app code, tests, and validation. This workspace does not use OpenSpec or
repository spec trees; durable rules live in `AGENTS.md`. Use `$pingou-env` for
the workspace lifecycle.

Work directly in the primary checkout and primary branch of every repository:
`main` for the parent, backend, frontend, and landing repositories, and
`master` for the chat repository while that remains its upstream primary
branch. Do not create feature branches or Git worktrees unless this temporary
preference is explicitly changed.

After cloning, initialize submodules:

```bash
git submodule update --init --recursive
```

The root `.env` points Compose at these primary child checkouts. If parallel
workers are explicitly requested, give them disjoint file ownership and
coordinate their edits in the same primary checkout.

## Fixture-backed development data

`pingou-o-que-backend/apps/api/fixtures/financial_seed.json` is the single
source for bootstrap, demo, and local domain data. `make up` and `make seed`
load it through the backend's idempotent fixture loader. Runtime-created state,
such as real chat sessions, remains runtime state.

Every backend model, relationship, business-state, or create/mutate-flow change
must update that fixture and `apps/core/tests/test_seed.py` in the same child
repository change. Keep 10-20 representative records per domain model or new
business flow; relationship-generated rows may exceed that when needed, while
fixed infrastructure identities may remain singletons. Do not introduce
bootstrap data through migrations, startup hooks, service defaults, or ad hoc
scripts.
