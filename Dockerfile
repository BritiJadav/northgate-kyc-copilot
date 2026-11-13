# ============================================================
# Stage 1: Build the React + Vite Frontend
# ============================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Python 3.13 Backend + Production Static Bundle
# ============================================================
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies required for Pillow, ReportLab, and networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install backend Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code and config
COPY backend/ ./backend/
COPY pytest.ini Makefile ./

# Copy built frontend dist from Stage 1 into frontend/dist
COPY --from=frontend-builder /build/dist ./frontend/dist

# Copy entrypoint script
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV DEMO_MODE=true
ENV APP_ENV=production
ENV PYTHONPATH=/app
ENV DATA_DIR=/app/backend/data
ENV DATABASE_URL=sqlite:////app/backend/data/northgate_kyc.db

# Seed initial database and generate synthetic documents at build time
RUN python -m backend.app.seed.seed_data

# Cloud Run injects $PORT (defaults to 8080)
EXPOSE 8080

ENTRYPOINT ["/app/docker-entrypoint.sh"]
