.PHONY: help build up upb down logs test lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


build: ## Build all services
	docker-compose build

up: ## Start all services
	docker-compose up -d

upb: ## Build and start all services
	docker-compose up --build -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

test: ## Run tests inside docker-compose.test stack
	@COMPOSE_FILE=docker-compose.test.yml; \
	docker-compose -f $$COMPOSE_FILE up --build --abort-on-container-exit --exit-code-from tests; \
	exit_code=$$?; \
	docker-compose -f $$COMPOSE_FILE down -v; \
	exit $$exit_code


lint: ## Run linting
	ruff format .
