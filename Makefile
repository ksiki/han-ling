DC_FILE = deploy/docker-compose.yml
DC = docker compose -f $(DC_FILE)
AUTH_DIR = auth_service
MESSAGE ?= "migration"

.PHONY: up down restart build logs ps auth-upgrade auth-revision auth-downgrade auth-logs db-shell redis-cli pre-commit setup

up:
	$(DC) up -d

down:
	$(DC) down

restart: down up

build:
	$(DC) build

logs:
	$(DC) logs -f

ps:
	$(DC) ps

auth-upgrade:
	cd $(AUTH_DIR) && poetry run alembic upgrade head

auth-revision:
	cd $(AUTH_DIR) && poetry run alembic revision --autogenerate -m "$(MESSAGE)"

auth-downgrade:
	cd $(AUTH_DIR) && poetry run alembic downgrade -1

auth-logs:
	$(DC) logs -f auth_service

db-logs:
	$(DC) logs -f database

db-shell:
	$(DC) exec database sh -c 'psql -U $$POSTGRES_USER -d $$POSTGRES_DB'

redis-cli:
	$(DC) exec redis redis-cli

pre-commit:
	pre-commit run --all-files

setup:
	pre-commit install
	cd $(AUTH_DIR) && poetry install
