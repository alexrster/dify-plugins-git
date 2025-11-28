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
		dify plugin package . -o dist/git-integration-plugin.difypkg; \
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

sign: build ## Build and sign the plugin package
	@if [ ! -f git-integration-keypair.private.pem ]; then \
		echo "Private key not found. Generating key pair..."; \
		dify signature generate -f git-integration-keypair; \
		echo "Key pair generated. Keep git-integration-keypair.private.pem secure!"; \
	fi
	@if [ -f dist/git-integration-plugin.difypkg ]; then \
		echo "Signing plugin..."; \
		dify signature sign dist/git-integration-plugin.difypkg -p git-integration-keypair.private.pem; \
		echo "Plugin signed: dist/git-integration-plugin.signed.difypkg"; \
		dify signature verify dist/git-integration-plugin.signed.difypkg -p git-integration-keypair.public.pem; \
	else \
		echo "Error: Plugin package not found. Run 'make build' first."; \
		exit 1; \
	fi

generate-keys: ## Generate signing key pair
	dify signature generate -f git-integration-keypair
	@echo "Key pair generated:"
	@echo "  Private key: git-integration-keypair.private.pem (KEEP SECRET!)"
	@echo "  Public key: git-integration-keypair.public.pem (share with Dify)"

verify-signature: ## Verify plugin signature
	@if [ ! -f dist/git-integration-plugin.signed.difypkg ]; then \
		echo "Error: Signed plugin not found. Run 'make sign' first."; \
		exit 1; \
	fi
	@if [ ! -f git-integration-keypair.public.pem ]; then \
		echo "Error: Public key not found. Run 'make generate-keys' first."; \
		exit 1; \
	fi
	dify signature verify dist/git-integration-plugin.signed.difypkg -p git-integration-keypair.public.pem

ci: lint test security ## Run all CI checks locally

pre-commit: format lint test ## Run pre-commit checks


