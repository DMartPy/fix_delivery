.PHONY: help install install-dev format lint lint-fix test clean docker-up docker-down docker-restart

help: ## Показать справку по командам
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости проекта
	poetry install --only=main

install-dev: ## Установить зависимости для разработки
	poetry install
	pre-commit install

format: ## Форматировать код (black + isort)
	poetry run black src/
	poetry run isort src/

lint: ## Проверить код (ruff)
	poetry run ruff check src/

lint-fix: ## Исправить проблемы с кодом (ruff --fix)
	poetry run ruff check --fix src/

test: ## Запустить тесты
	poetry run pytest

test-verbose: ## Запустить тесты с подробным выводом
	poetry run pytest -v

test-coverage: ## Запустить тесты с покрытием
	poetry run pytest --cov=src/dostavka --cov-report=html --cov-report=term

test-fast: ## Запустить только быстрые тесты
	poetry run pytest -m "not slow"

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

docker-up: ## Запустить Docker сервисы
	docker-compose -f docker-compose-local.yaml up -d

docker-down: ## Остановить Docker сервисы
	docker-compose -f docker-compose-local.yaml down

docker-restart: ## Перезапустить Docker сервисы
	docker-compose -f docker-compose-local.yaml restart

docker-logs: ## Показать логи Docker сервисов
	docker-compose -f docker-compose-local.yaml logs -f

check-all: format lint ## Форматировать и проверить код

pre-commit-all: ## Запустить все pre-commit hooks
	pre-commit run --all-files