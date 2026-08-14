# ============================================
# BMKG Data Platform — DX shortcuts
# ============================================
# Common commands wrapped around docker compose.
# ============================================

SHELL := /bin/bash
STACK ?=
COMPOSE := docker compose
ifeq ($(STACK),)
	COMPOSE += --profile phase-1
else
	COMPOSE += --profile $(STACK)
endif

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: up
up: ## Bring up services for current phase (default: phase-1)
	$(COMPOSE) up -d
	@echo "Stack is up. Run 'make logs' to follow."

.PHONY: down
down: ## Stop and remove services
	$(COMPOSE) down

.PHONY: down-v
down-v: ## Stop and remove services + volumes (DESTRUCTIVE)
	$(COMPOSE) down -v

.PHONY: logs
logs: ## Follow logs
	$(COMPOSE) logs -f --tail=100

.PHONY: ps
ps: ## List running services
	$(COMPOSE) ps

.PHONY: lint
lint: ## Run ruff linter + formatter check
	ruff check .
	ruff format --check .

.PHONY: fmt
fmt: ## Auto-format code
	ruff format .
	ruff check --fix .

.PHONY: test
test: ## Run unit tests
	pytest

.PHONY: phase-1-up
phase-1-up: ## Explicit: bring up Phase 1 stack
	docker compose --profile phase-1 up -d

.PHONY: phase-1-logs-ingestion
phase-1-logs-ingestion: ## Follow ingestion logs
	docker compose --profile phase-1 logs -f ingestion

.PHONY: minio-console
minio-console: ## Print MinIO console URL
	@echo "MinIO Console: http://localhost:$${MINIO_CONSOLE_PORT:-9001}"
