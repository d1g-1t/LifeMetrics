.PHONY: help setup start stop restart logs clean test migrate shell build rebuild down ps init-db
.DEFAULT_GOAL := help

DC := docker compose

help:
	@echo "LifeMetrics Commands:"
	@echo "  make setup    - Full setup (build + start)"
	@echo "  make start    - Start all services"
	@echo "  make stop     - Stop all services"
	@echo "  make logs     - Show logs"
	@echo "  make shell    - Django shell"
	@echo "  make migrate  - Run migrations"
	@echo "  make init-db  - Initialize database"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove all containers and volumes"

setup:
	@echo "Creating .env file..."
	@test -f .env || cp .env.example .env
	@echo "Stopping old containers..."
	@$(DC) down --remove-orphans 2>/dev/null || true
	@echo "Building images..."
	@$(DC) build
	@echo "Starting services..."
	@$(DC) up -d
	@echo "Waiting for database..."
	@sleep 10
	@echo "Running migrations..."
	@$(DC) exec -T web python manage.py migrate --noinput || true
	@echo ""
	@echo "Setup complete!"
	@echo "  API: http://localhost:8000/api/docs"
	@echo "  Admin: http://localhost:8000/admin"
	@echo ""
	@echo "Next: make init-db (to create superuser)"

start:
	@$(DC) up -d
	@echo "Services started: http://localhost:8000"

stop:
	@$(DC) stop

restart:
	@$(DC) restart

down:
	@$(DC) down

logs:
	@$(DC) logs -f

logs-web:
	@$(DC) logs -f web

logs-bot:
	@$(DC) logs -f telegram_bot

ps:
	@$(DC) ps

build:
	@$(DC) build

rebuild:
	@$(DC) build --no-cache

migrate:
	@$(DC) exec web python manage.py migrate

makemigrations:
	@$(DC) exec web python manage.py makemigrations

init-db:
	@$(DC) exec web python manage.py migrate
	@$(DC) exec web python manage.py createsuperuser

superuser:
	@$(DC) exec web python manage.py createsuperuser

shell:
	@$(DC) exec web python manage.py shell

test:
	@$(DC) exec web pytest -v

lint:
	@$(DC) exec web python -m ruff check apps/

format:
	@$(DC) exec web python -m ruff format apps/

bot-restart:
	@$(DC) restart telegram_bot

celery-restart:
	@$(DC) restart celery_worker celery_beat

db-shell:
	@$(DC) exec db psql -U lifemetrics_user -d lifemetrics

db-backup:
	@mkdir -p backups
	@$(DC) exec -T db pg_dump -U lifemetrics_user lifemetrics > backups/backup_$$(date +%Y%m%d_%H%M%S).sql

clean:
	@$(DC) down -v --remove-orphans
	@docker system prune -f
