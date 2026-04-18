.PHONY: help build up down logs seed clean dev-backend dev-frontend

help: ## Show this help message
@echo 'Usage: make [target]'
@echo ''
@echo 'Available targets:'
@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build all Docker containers
docker-compose build

up: ## Start all services
docker-compose up -d

down: ## Stop all services
docker-compose down

logs: ## View logs from all services
docker-compose logs -f

seed: ## Seed database with initial data
docker-compose exec backend python -c "from app.db.session import SessionLocal; from app.db.seed_data import seed_all; db = SessionLocal(); seed_all(db); db.close()"

clean: ## Remove all containers and volumes
docker-compose down -v --remove-orphans

dev-backend: ## Run backend locally for development
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload

dev-frontend: ## Run frontend locally for development
cd frontend && npm install && npm run dev

restart: ## Restart all services
docker-compose restart

status: ## Show status of all services
docker-compose ps

backend-shell: ## Open shell in backend container
docker-compose exec backend bash

db-shell: ## Open psql shell in database container
docker-compose exec db psql -U pylearn -d pylearn_db

redis-cli: ## Open Redis CLI
docker-compose exec redis redis-cli
