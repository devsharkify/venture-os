# Stage 1: Build React frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/scripts/ ./scripts/
RUN npm install --legacy-peer-deps
COPY frontend/ ./
ENV REACT_APP_BACKEND_URL=
ENV DISABLE_ESLINT_PLUGIN=true
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

# Install WeasyPrint system dependencies (pango, cairo for PDF generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
    libffi-dev shared-mime-info \
    fonts-noto fonts-noto-cjk fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

COPY backend/ .

# Copy React build to /frontend/build (server.py FRONTEND_BUILD = /frontend/build)
COPY --from=frontend-builder /frontend/build /frontend/build

CMD ["/bin/sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}"]
