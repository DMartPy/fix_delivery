# 🛠️ Руководство разработчика

## 📋 Требования

- Python 3.9+
- Poetry
- Docker & Docker Compose
- Make (опционально, для Windows используйте команды напрямую)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Только основные зависимости
poetry install --only=main

# Все зависимости (включая dev)
poetry install
```

### 2. Установка pre-commit hooks

```bash
poetry install  # если еще не установили
pre-commit install
```

### 3. Запуск сервисов

```bash
# Через Makefile
make docker-up

# Или напрямую
docker-compose -f docker-compose-local.yaml up -d
```

## 🧹 Качество кода

### Автоматическое форматирование

```bash
# Форматировать код
make format

# Или отдельно
poetry run black src/
poetry run isort src/
```

### Проверка качества

```bash
# Проверить код
make lint

# Исправить автоматически исправимые проблемы
make lint-fix

# Запустить все проверки
make check-all
```

### Pre-commit hooks

Pre-commit hooks автоматически запускаются при каждом коммите и проверяют:

- Форматирование кода (black)
- Сортировку импортов (isort)
- Качество кода (ruff)
- Базовые проверки (trailing whitespace, YAML, etc.)

```bash
# Запустить все hooks вручную
make pre-commit-all

# Или
pre-commit run --all-files
```

## 🔧 Инструменты

### Ruff

Быстрый линтер Python, заменяет flake8, isort, pyupgrade и другие.

**Конфигурация:** `pyproject.toml` секция `[tool.ruff]`

**Основные правила:**
- E, W - pycodestyle (PEP 8)
- F - pyflakes (логические ошибки)
- I - isort (сортировка импортов)
- B - flake8-bugbear (потенциальные ошибки)
- C4 - flake8-comprehensions (списковые включения)
- UP - pyupgrade (современный синтаксис)

### Black

Автоматический форматировщик кода.

**Конфигурация:** `pyproject.toml` секция `[tool.black]`

**Особенности:**
- Длина строки: 88 символов
- Минимальная версия Python: 3.9
- Совместим с isort

### isort

Сортировка и группировка импортов.

**Конфигурация:** `pyproject.toml` секция `[tool.isort]`

**Профиль:** black (совместимость с Black)

## 📁 Структура проекта

```
dostavka/
├── src/
│   └── dostavka/
│       ├── api/           # API endpoints
│       ├── celery/        # Celery tasks
│       ├── core/          # Core functionality
│       ├── db/            # Database models & DAL
│       ├── redis/         # Redis cache
│       └── services/      # Business logic
├── .pre-commit-config.yaml
├── pyproject.toml
├── Makefile
└── docker-compose-local.yaml
```

## 🐳 Docker команды

```bash
# Запуск
make docker-up

# Остановка
make docker-down

# Перезапуск
make docker-restart

# Логи
make docker-logs
```

## 🧪 Тестирование

```bash
# Запуск тестов
make test

# Или
poetry run pytest
```

## 🧹 Очистка

```bash
# Очистить временные файлы
make clean

# Очистить Docker
make docker-down
docker system prune -f
```

## 📝 Workflow разработки

1. **Создание ветки**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Разработка**
   - Пишите код
   - Периодически форматируйте: `make format`
   - Проверяйте качество: `make lint`

3. **Подготовка к коммиту**
   ```bash
   make check-all  # форматирование + проверка
   ```

4. **Коммит**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # pre-commit hooks запустятся автоматически
   ```

5. **Push и Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## ⚠️ Troubleshooting

### Pre-commit не работает

```bash
# Переустановить hooks
pre-commit uninstall
pre-commit install
```

### Ruff ошибки

```bash
# Показать все проблемы
poetry run ruff check src/ --output-format=text

# Автоматически исправить
poetry run ruff check --fix src/
```

### Black конфликты

```bash
# Принудительно переформатировать
poetry run black src/ --force-exclude
```

## 🔗 Полезные ссылки

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
