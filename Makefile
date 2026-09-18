DC_FILE = deploy/docker-compose.yaml
DC = docker compose -f $(DC_FILE)
AUTH_DIR = auth_service
MESSAGE ?= "migration"

.PHONY: up down restart build logs ps auth-upgrade auth-revision auth-downgrade auth-logs auth-test db-up db-logs db-shell redis-cli pre-commit setup mypy check

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
	cd $(AUTH_DIR) && POSTGRES_HOST=localhost poetry run alembic upgrade head

auth-revision:
	cd $(AUTH_DIR) && POSTGRES_HOST=localhost poetry run alembic revision --autogenerate -m "$(MESSAGE)"

auth-downgrade:
	cd $(AUTH_DIR) && POSTGRES_HOST=localhost poetry run alembic downgrade -1

auth-logs:
	$(DC) logs -f auth_service

auth-test:
	cd $(AUTH_DIR) && poetry run pytest --cov=src --cov-report=html

db-up:
	$(DC) up -d database

db-logs:
	$(DC) logs -f database

db-shell:
	$(DC) exec database sh -c 'psql -U $$POSTGRES_USER -d $$POSTGRES_DB'

redis-cli:
	$(DC) exec redis redis-cli

pre-commit:
	pre-commit run --all-files

mypy:
	cd $(AUTH_DIR) && poetry run mypy .

check: pre-commit mypy

setup:
	pre-commit install
	cd $(AUTH_DIR) && poetry install
