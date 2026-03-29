.PHONY: help setup start stop restart status logs download-models clean

SHELL := /bin/zsh
VENV := .venv
PYTHON := $(VENV)/bin/python
UVICORN := $(VENV)/bin/uvicorn
DASHBOARD_PORT := 8502
DASHBOARD_PID := /tmp/mlx-dashboard.pid
DASHBOARD_LOG := /tmp/mlx-dashboard.log

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Full lifecycle ===

setup: ## Initial setup: venv + dependencies
	uv venv
	uv pip install -e ".[dev]"
	@echo "\n✓ Setup complete. Run 'make download-models' to fetch models."

start: ## Start dashboard server
	@if curl -s http://localhost:$(DASHBOARD_PORT)/api/system/health > /dev/null 2>&1; then \
		echo "Dashboard already running"; \
	else \
		echo "Starting MLX Dashboard..."; \
		$(UVICORN) app.main:app --host 0.0.0.0 --port $(DASHBOARD_PORT) \
			> $(DASHBOARD_LOG) 2>&1 & echo $$! > $(DASHBOARD_PID); \
		sleep 2; \
		echo "Dashboard: http://localhost:$(DASHBOARD_PORT)"; \
	fi

stop: ## Stop dashboard server
	@if [ -f $(DASHBOARD_PID) ]; then \
		kill $$(cat $(DASHBOARD_PID)) 2>/dev/null && echo "Dashboard stopped" || echo "Dashboard not running"; \
		rm -f $(DASHBOARD_PID); \
	else \
		echo "Dashboard not running"; \
	fi

restart: stop start ## Restart dashboard

status: ## Show status
	@echo "=== MLX Dashboard ==="
	@if curl -s http://localhost:$(DASHBOARD_PORT)/api/system/health > /dev/null 2>&1; then \
		echo "  Status: running (http://localhost:$(DASHBOARD_PORT))"; \
	else \
		echo "  Status: stopped"; \
	fi
	@echo "\n=== Downloaded Models ==="
	@$(PYTHON) -c "from app.services.mlx_client import list_models; [print(f'  {m[\"name\"]:20s} {\"✓\" if m[\"downloaded\"] else \"✗\"}') for m in list_models()]" 2>/dev/null || echo "  (run 'make setup' first)"

logs: ## Show dashboard logs
	@tail -f $(DASHBOARD_LOG)

# === Models ===

download-models: ## Download all models (first run triggers HuggingFace download)
	@echo "Downloading models via MLX-LM (this may take a while)..."
	@for model in \
		mlx-community/Llama-3.2-3B-Instruct-4bit \
		mlx-community/Llama-3.1-8B-Instruct-4bit \
		mlx-community/Qwen2.5-Coder-7B-Instruct-4bit \
		mlx-community/Qwen2.5-7B-Instruct-4bit \
		mlx-community/DeepSeek-R1-Distill-Llama-8B-4bit \
		mlx-community/Mistral-7B-Instruct-v0.3-4bit \
		mlx-community/Qwen2.5-32B-Instruct-4bit; do \
		echo "\n--- Downloading $$model ---"; \
		$(PYTHON) -c "from mlx_lm import load; load('$$model')"; \
	done
	@echo "\n✓ All models downloaded"

# === Cleanup ===

clean: stop ## Stop and remove generated data
	rm -f $(DASHBOARD_PID) $(DASHBOARD_LOG)
	rm -f app/data/results.json
	@echo "✓ Cleaned up"
