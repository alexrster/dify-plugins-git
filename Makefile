.PHONY: help install install-dev test lint format security clean build package

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	pytest-watch tests/

lint: ## Run all linters
	flake8 . --count --statistics
	black --check .
	isort --check-only .
	pylint endpoints/ services/ models/ utils/ main.py || true
	mypy . || true

format: ## Format code
	black .
	isort .

security: ## Run security checks
	bandit -r . -ll
	safety check

clean: ## Clean build artifacts
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build the plugin package
	mkdir -p dist
	@if command -v dify &> /dev/null; then \
		dify plugin package . -o dist/; \
	else \
		echo "Dify CLI not available, creating manual package"; \
		tar -czf dist/git-integration-plugin.tar.gz \
			--exclude='.git' \
			--exclude='tests' \
			--exclude='.github' \
			--exclude='*.pyc' \
			--exclude='__pycache__' \
			--exclude='.pytest_cache' \
			--exclude='dist' \
			--exclude='*.egg-info' \
			--exclude='.env' \
			. ; \
	fi

package: build ## Alias for build

ci: lint test security ## Run all CI checks locally

pre-commit: format lint test ## Run pre-commit checks


