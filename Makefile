.DEFAULT_GOAL := help
.PHONY: help install test typecheck check run clean

help:  ## Show available commands
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install:  ## Sync the virtualenv with the lockfile
	uv sync

test:  ## Run the test suite
	uv run pytest

typecheck:  ## Type-check source and tests
	uv run mypy src tests

check: test typecheck  ## Run tests and type check

run:  ## Run the CLI on a file: make run FILE=reads.fastq
	@test -n "$(FILE)" || { echo 'usage: make run FILE=<path>'; exit 1; }
	uv run lungfish $(FILE)

clean:  ## Remove caches and build artifacts
	rm -rf .mypy_cache .pytest_cache build dist
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
