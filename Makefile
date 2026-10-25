.PHONY: install format lint test run-api run-frontend clean

install:
	pip install --upgrade pip
	pip install -r requirements-dev.txt

format:
	black src api frontend tests
	ruff check --fix src api frontend tests

lint:
	black --check src api frontend tests
	ruff check src api frontend tests

test:
	pytest tests/

run-api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/app.py --server.port 8501

clean:
	rm -rf __pycache__ .pytest_cache .coverage .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
