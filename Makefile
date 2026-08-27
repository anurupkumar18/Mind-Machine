API_DIR := apps/api
WEB_DIR := apps/web

.PHONY: setup dev test lint typecheck check smoke demo memory-check

setup:
	cd $(API_DIR) && uv sync --dev
	cd $(WEB_DIR) && pnpm install --ignore-scripts

dev:
	@echo "Run 'cd apps/api && uv run uvicorn app.main:app --reload' and 'cd apps/web && pnpm dev' in separate terminals."

test:
	cd $(API_DIR) && uv run pytest
	cd $(WEB_DIR) && pnpm test

lint:
	cd $(API_DIR) && uv run ruff check .
	cd $(WEB_DIR) && pnpm lint

typecheck:
	cd $(API_DIR) && uv run mypy app
	cd $(WEB_DIR) && pnpm typecheck

memory-check:
	python3 scripts/memory_check.py

smoke:
	cd $(API_DIR) && uv run pytest tests/test_api.py -q

check: memory-check lint typecheck test smoke

demo: check
	@echo "Demo ready: start API and web, then follow docs/DEMO_RUNBOOK.md."
