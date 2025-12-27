# Meeting Copilot - Makefile
# Developed by Ruslan Magana (contact@ruslanmv.com)

.PHONY: help install run clean test dev lint format check-env

# Python version requirement
PYTHON_VERSION := 3.11
UV := uv

# Colors for help
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Meeting Copilot - Voice Assistant for Meetings$(NC)"
	@echo "$(GREEN)Developed by: Ruslan Magana (contact@ruslanmv.com)$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies using uv and Python 3.11
	@echo "$(BLUE)Installing Meeting Copilot...$(NC)"
	@command -v $(UV) >/dev/null 2>&1 || { echo "$(YELLOW)uv not found. Installing uv...$(NC)"; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "$(GREEN)Creating virtual environment with Python $(PYTHON_VERSION)...$(NC)"
	$(UV) venv --python $(PYTHON_VERSION)
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(UV) pip install -e .
	@echo "$(GREEN)Installation complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Copy .env.example to .env and configure your API keys"
	@echo "  2. Run 'make run' to start the application"

run: check-env ## Run the meeting copilot application
	@echo "$(BLUE)Starting Meeting Copilot...$(NC)"
	$(UV) run python -m meeting_copilot.app

dev: ## Run in development mode with auto-reload
	@echo "$(BLUE)Starting Meeting Copilot in development mode...$(NC)"
	$(UV) run python -m meeting_copilot.app --dev

console: ## Run minimal console version (no UI)
	@echo "$(BLUE)Starting Meeting Copilot console mode...$(NC)"
	$(UV) run python -m meeting_copilot.app --console

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(UV) run pytest tests/ -v

lint: ## Run code linting
	@echo "$(BLUE)Running linters...$(NC)"
	$(UV) run ruff check src/

format: ## Format code with black and ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	$(UV) run ruff format src/
	$(UV) run ruff check --fix src/

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/
	@echo "$(GREEN)Cleanup complete!$(NC)"

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: .env file not found!$(NC)"; \
		echo "$(YELLOW)Copy .env.example to .env and configure your API keys.$(NC)"; \
		if [ -f .env.example ]; then \
			echo "$(GREEN)Creating .env from .env.example...$(NC)"; \
			cp .env.example .env; \
			echo "$(YELLOW)Please edit .env and add your API keys before running.$(NC)"; \
		fi; \
	fi

setup: install check-env ## Complete setup (install + env check)
	@echo "$(GREEN)Setup complete! You're ready to go.$(NC)"
	@echo "$(YELLOW)Remember to configure your .env file with API keys.$(NC)"

build: ## Build distributable package
	@echo "$(BLUE)Building package...$(NC)"
	$(UV) build

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(UV) pip install -e ".[dev]"

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "Documentation will be available in docs/"

update: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(UV) pip install --upgrade -e .

freeze: ## Show installed packages
	$(UV) pip freeze

info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Name: Meeting Copilot"
	@echo "  Developer: Ruslan Magana"
	@echo "  Contact: contact@ruslanmv.com"
	@echo "  Python: $(PYTHON_VERSION)"
	@echo "  Package Manager: uv"
