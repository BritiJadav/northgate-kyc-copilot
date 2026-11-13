#!/bin/bash
set -e

# If SQLite DB or documents do not exist in the volume or runtime directory, seed them
if [ ! -f "/app/backend/data/northgate_kyc.db" ]; then
    echo "Database not found. Initializing SQLite tables and synthetic document assets..."
    python -m backend.app.seed.seed_data
fi

echo "============================================================"
echo "Starting Northgate KYC Copilot (GCP Cloud Run Container)"
echo "Port: ${PORT:-8080}"
echo "Model: ${GEMINI_MODEL:-gemini-2.5-flash}"
echo "Demo Mode: ${DEMO_MODE:-true}"
echo "============================================================"

# Launch Uvicorn server binding to 0.0.0.0 and Cloud Run injected PORT
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
