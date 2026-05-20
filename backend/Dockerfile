FROM python:3.11-slim

WORKDIR /app

# Install WeasyPrint system dependencies (pango, cairo for PDF generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
    libffi-dev shared-mime-info \
    fonts-noto fonts-noto-cjk fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

COPY . .

CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
