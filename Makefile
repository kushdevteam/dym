.PHONY: help setup build up down logs clean test

help: ## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "Setting up project..."
	@cp .env.example .env
	@echo "Please edit .env file with your API keys and configuration"

build: ## Build all containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

logs-api: ## Show API logs
	docker-compose logs -f api

logs-dashboard: ## Show dashboard logs
	docker-compose logs -f dashboard

logs-db: ## Show database logs
	docker-compose logs -f postgres

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

test: ## Run tests
	@echo "Running tests..."
	@echo "No tests implemented yet"

dev: ## Start development environment
	@echo "Starting development environment..."
	@echo "Make sure to run 'make setup' first if this is your first time"
	docker-compose up

db-init: ## Initialize database
	docker-compose exec postgres psql -U postgres -d narrative_scanner -f /docker-entrypoint-initdb.d/init.sql

db-shell: ## Access database shell
	docker-compose exec postgres psql -U postgres -d narrative_scanner

api-shell: ## Access API container shell
	docker-compose exec api bash

dashboard-shell: ## Access dashboard container shell
	docker-compose exec dashboard sh

install-deps: ## Install all dependencies
	@echo "Installing API dependencies..."
	cd api && pip install -r requirements.txt
	@echo "Installing dashboard dependencies..."
	cd dashboard && npm install