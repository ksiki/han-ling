DC_FILE = deploy/docker-compose.yaml
DC = docker compose -f $(DC_FILE)
AUTH_DIR = auth_service
CONTENT_DIR = content_service
MESSAGE ?= "migration"

.PHONY: up down restart build ps auth-upgrade auth-revision auth-downgrade auth-test content-upgrade content-revision content-downgrade content-test db-up pre-commit setup mypy check

up:
	$(DC) up -d

down:
	$(DC) down

restart: down up

build:
	$(DC) build

ps:
	$(DC) ps

auth-upgrade:
	cd $(AUTH_DIR) && POSTGRES_HOST=localhost poetry run alembic upgrade head

auth-revision:
	cd $(AUTH_DIR) && POSTGRES_HOST=localhost poetry run alembic revision --autogenerate -m "$(MESSAGE)"

auth-downgrade:
	cd $(AUTH_DIR) && POSTGRES_HOST=localhost poetry run alembic downgrade -1

auth-test:
	cd $(AUTH_DIR) && poetry run pytest --cov=src --cov-report=html

content-upgrade:
	cd $(CONTENT_DIR) && POSTGRES_HOST=localhost poetry run alembic upgrade head

content-revision:
	cd $(CONTENT_DIR) && POSTGRES_HOST=localhost poetry run alembic revision --autogenerate -m "$(MESSAGE)"

content-downgrade:
	cd $(CONTENT_DIR) && POSTGRES_HOST=localhost poetry run alembic downgrade -1

content-test:
	cd $(CONTENT_DIR) && poetry run pytest --cov=src --cov-report=html

db-up:
	$(DC) up -d database

pre-commit:
	pre-commit run --all-files

mypy:
	cd $(AUTH_DIR) && poetry run mypy .

check: pre-commit mypy

setup:
	pre-commit install
	cd $(AUTH_DIR) && poetry install
	cd $(CONTENT_DIR) && poetry install
