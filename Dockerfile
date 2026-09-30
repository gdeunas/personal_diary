FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем системные утилиты, необходимые для сборки некоторых питон-пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и собираем wheels-пакеты в локальную директорию
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем только библиотеку libpq, необходимую для работы PostgreSQL драйвера (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем собранные бинарники зависимостей с этапа сборщика и устанавливаем их
COPY --from=builder /app/wheels /brightness/wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /brightness/wheels/*

# Создаем директории для статики и медиафайлов
RUN mkdir -p /app/staticfiles /app/mediafiles

# Копируем исходный код всего приложения Django в контейнер
COPY . .

# Создаем безопасного системного пользователя, чтобы не запускать приложение от root
RUN useradd -U appuser && \
    chown -R appuser:appuser /app

# Переключаемся на созданного пользователя
USER appuser

# Открываем порт, на котором gunicorn будет слушать запросы внутри Docker-сети
EXPOSE 8000
