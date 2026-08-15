ENV_FILE ?= .env
ENV_NAME ?=
WAIT_TIMEOUT ?= 300
SERVICE ?=
ARGS ?=
PYTHON ?= python3

COMPOSE = docker compose --env-file "$(ENV_FILE)" --file compose.yaml

.NOTPARALLEL: build up

.PHONY: env-init config build build-backend build-chat build-frontend build-landing up dev watch stop down destroy ps logs restart portless-up portless-down urls doctor migrate seed manage shell db-shell redis-cli scheduler flower

env-init:
	@$(PYTHON) -m tools.dev.init_env --env-file "$(ENV_FILE)" $(if $(ENV_NAME),--env-name "$(ENV_NAME)",)

config:
	@$(COMPOSE) config

build: build-backend build-chat build-frontend build-landing

build-backend:
	$(COMPOSE) build api

build-chat:
	$(COMPOSE) build chat

build-frontend:
	$(COMPOSE) build frontend

build-landing:
	$(COMPOSE) build landing

up: build
	$(COMPOSE) up --detach --wait --wait-timeout $(WAIT_TIMEOUT)
	$(COMPOSE) exec -T api python scripts/seed.py
	@$(PYTHON) -m tools.dev.portless_routes add --env-file "$(ENV_FILE)"

dev: up
	$(COMPOSE) watch

watch:
	$(COMPOSE) watch

stop:
	$(COMPOSE) stop $(SERVICE)

down:
	$(COMPOSE) down --remove-orphans
	@$(PYTHON) -m tools.dev.portless_routes remove --env-file "$(ENV_FILE)"

destroy:
	$(COMPOSE) down --remove-orphans --volumes --rmi local
	@$(PYTHON) -m tools.dev.portless_routes remove --env-file "$(ENV_FILE)"

ps:
	@$(COMPOSE) ps --all

logs:
	$(COMPOSE) logs --follow --tail=200 $(SERVICE)

restart:
	$(COMPOSE) restart $(SERVICE)

portless-up:
	@$(PYTHON) -m tools.dev.portless_routes add --env-file "$(ENV_FILE)"

portless-down:
	@$(PYTHON) -m tools.dev.portless_routes remove --env-file "$(ENV_FILE)"

urls:
	@$(PYTHON) -m tools.dev.portless_routes show --env-file "$(ENV_FILE)"

doctor:
	@docker info >/dev/null
	@portless doctor

migrate: build-backend
	$(COMPOSE) run --rm -e DJANGO_MIGRATE=0 api python manage.py migrate --no-input

seed: build-backend
	$(COMPOSE) run --rm api python scripts/seed.py

manage: build-backend
	$(COMPOSE) run --rm api python manage.py $(ARGS)

shell:
	$(COMPOSE) exec api sh

db-shell:
	$(COMPOSE) exec db sh -c 'psql -U "$$POSTGRES_USER" "$$POSTGRES_DB"'

redis-cli:
	$(COMPOSE) exec redis redis-cli

scheduler: build-backend
	$(COMPOSE) --profile scheduler up --detach --wait celery-beat

flower: build-backend
	$(COMPOSE) --profile observability up --detach --wait flower
	@$(PYTHON) -m tools.dev.portless_routes add --env-file "$(ENV_FILE)" --services flower
