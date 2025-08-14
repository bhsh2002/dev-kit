POETRY=poetry
PY=python

.PHONY: install test lint format typecheck seed migrate-up pre-commit example

install:
	$(POETRY) install --no-interaction --no-root

test:
	$(POETRY) run pytest

lint:
	$(POETRY) run ruff check src tests

format:
	$(POETRY) run ruff check --fix src tests
	$(POETRY) run black src tests

typecheck:
	$(POETRY) run mypy src

pre-commit:
	$(POETRY) run pre-commit install

seed:
	$(POETRY) run dev-kit-seed-auth --admin-username admin --admin-password change-me

migrate-up:
	SQLALCHEMY_DATABASE_URI=sqlite:///devkit.db alembic upgrade head

example:
	$(POETRY) run $(PY) -m dev_kit.example_app
