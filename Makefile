.PHONY: help install test lint format clean setup-db run-streamlit

help:
	@echo "Sports Analytics System - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install          Install dependencies"
	@echo "  make setup-env        Create .env from .env.example"
	@echo "  make test             Run all tests with coverage"
	@echo "  make lint             Run linting checks (flake8, mypy)"
	@echo "  make format           Format code with black"
	@echo "  make clean            Remove build artifacts and caches"
	@echo ""
	@echo "Database:"
	@echo "  make setup-db         Initialize PostgreSQL database"
	@echo ""
	@echo "Running:"
	@echo "  make run-streamlit    Start Streamlit dashboard"

install:
	pip install -r requirements.txt

setup-env:
	test -f .env || cp .env.example .env
	@echo "✓ .env file created. Edit with your credentials."

test:
	pytest tests/ -v --cov=src --cov-report=html
	@echo "✓ Tests completed. Coverage report in htmlcov/index.html"

lint:
	flake8 src tests --max-line-length=100 --ignore=E203,W503
	mypy src --ignore-missing-imports
	@echo "✓ Linting completed"

format:
	black src tests --line-length=100
	@echo "✓ Code formatted with black"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache
	@echo "✓ Cleaned up build artifacts"

setup-db:
	@echo "Note: Ensure PostgreSQL is running locally."
	python -m src.config --init-db
	@echo "✓ Database initialized"

run-streamlit:
	streamlit run src/visualization/dashboard.py
