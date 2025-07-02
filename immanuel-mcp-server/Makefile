# Makefile for Immanuel MCP Server

.PHONY: help install dev test lint format build clean docker-build docker-run docker-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies with uv"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  type-check  - Run type checking"
	@echo "  build       - Build package"
	@echo "  clean       - Clean build artifacts"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run Docker container"
	@echo "  docker-dev  - Run development Docker environment"

# Development setup
install:
	uv venv
	uv pip install -e .

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Testing
test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-integration:
	pytest -m integration

test-unit:
	pytest -m unit

# Code quality
lint:
	ruff app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	black app/ tests/
	isort app/ tests/
	ruff --fix app/ tests/

type-check:
	mypy app/

# Build and packaging
build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Docker commands
docker-build:
	docker build -t immanuel-mcp-server .

docker-run:
	docker run -p 8000:8000 immanuel-mcp-server

docker-dev:
	docker-compose --profile dev up -d

docker-prod:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Health checks
health:
	curl -f http://localhost:8000/health/ || exit 1

# Production deployment helpers
deploy-check:
	@echo "Running pre-deployment checks..."
	make test
	make lint
	make type-check
	@echo "All checks passed!"

# Database/Migration commands (if needed in future)
migrate:
	@echo "No migrations needed for current version"

# Backup/Restore (if needed in future)
backup:
	@echo "No backup needed for current version"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	# Add performance testing commands here

# Security scanning
security-scan:
	safety check
	bandit -r app/

# Documentation
docs:
	@echo "Documentation available in docs/ directory"
	@echo "API docs: http://localhost:8000/docs"

# Environment setup
setup-env:
	cp .env.example .env
	@echo "Environment file created. Please edit .env with your settings."

# CI/CD helpers
ci-test: install test lint type-check

ci-build: ci-test build docker-build

# Local development with all services
dev-full:
	docker-compose --profile dev --profile cache up -d

# Production deployment
deploy: deploy-check docker-build
	@echo "Ready for deployment!"

# Cleanup Docker resources
docker-clean:
	docker-compose down -v
	docker system prune -f