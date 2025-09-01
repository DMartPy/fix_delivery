# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости с retry логикой
RUN apt-get update --fix-missing || apt-get update --fix-missing && \
    apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы конфигурации Poetry
COPY pyproject.toml ./

# Настраиваем Poetry и устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-interaction --no-root

# Копируем исходный код
COPY src/ ./src/

# Устанавливаем переменную окружения для Docker
ENV DOCKER_ENV=true
ENV PYTHONPATH=/app/src

# Команда для запуска приложения
CMD ["python", "-m", "uvicorn", "dostavka.main:app", "--host", "0.0.0.0", "--port", "8000"]