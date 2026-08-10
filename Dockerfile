# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY accounts api applications config core messaging notifications profiles vacancies ./
# Основные зависимости — только из pyproject.toml (единственный источник)
RUN pip install --no-cache-dir --prefix=/install .

# Stage 2: Production image
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
