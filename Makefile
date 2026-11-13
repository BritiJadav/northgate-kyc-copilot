.PHONY: setup seed dev test eval record-cache docker-build docker-run

PYTHON ?= .venv/Scripts/python.exe
UVICORN ?= .venv/Scripts/uvicorn.exe
PYTEST ?= .venv/Scripts/pytest.exe

setup:
	@echo "Setting up virtual environment and dependencies..."
	python -m venv .venv
	$(PYTHON) -m pip install -r backend/requirements.txt
	cd frontend && npm install

seed:
	@echo "Generating synthetic PDFs and seeding database..."
	$(PYTHON) -m backend.app.seed.seed_data

dev:
	@echo "Starting backend and frontend development servers..."
	start cmd /k "$(UVICORN) backend.app.main:app --reload --port 8000"
	cd frontend && npm run dev

test:
	@echo "Running test suite..."
	$(PYTEST) backend/tests -v

eval:
	@echo "Running evaluation harness..."
	$(PYTHON) -m backend.eval.run_eval

record-cache:
	@echo "Recording live Gemini responses to demo cache..."
	$(PYTHON) backend/scripts/record_demo_cache.py

docker-build:
	@echo "Building production Docker image..."
	docker build -t northgate-kyc-copilot .

docker-run:
	@echo "Running production Docker container on http://localhost:8080..."
	docker run -p 8080:8080 --env PORT=8080 northgate-kyc-copilot
