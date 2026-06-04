# Bu dosya: İki aşamalı (multi-stage) Docker imaj tanımı
# Stage 1: builder
FROM python:3.11-slim AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim

COPY --from=builder /install /usr/local
WORKDIR /app
COPY app/ ./app/
COPY ui/ ./ui/

# Run as non-root user for security hardening
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
