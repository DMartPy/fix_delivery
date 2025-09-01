# 🧪 Тесты

## 📋 Описание

Тесты покрывают основные функции приложения:

- **API endpoints** - тестирование HTTP endpoints
- **Валидация данных** - проверка Pydantic моделей
- **Бизнес-логика** - расчет стоимости доставки
- **Модели** - тестирование Pydantic моделей

## 🚀 Запуск тестов

### Базовые команды

```bash
# Все тесты
make test

# Подробный вывод
make test-verbose

# С покрытием кода
make test-coverage

# Только быстрые тесты
make test-fast
```

### Напрямую через Poetry

```bash
# Все тесты
poetry run pytest

# Конкретный файл
poetry run pytest tests/test_api.py

# Конкретный тест
poetry run pytest tests/test_api.py::TestPackageEndpoints::test_get_package_types

# С маркерами
poetry run pytest -m "unit"
```

## 📁 Структура тестов

```
tests/
├── conftest.py          # Конфигурация и фикстуры
├── test_main.py         # Тесты основного приложения
├── test_api.py          # Тесты API endpoints
├── test_services.py     # Тесты бизнес-логики
└── test_models.py       # Тесты Pydantic моделей
```

## 🔧 Фикстуры

- `client` - синхронный тестовый клиент FastAPI
- `async_client` - асинхронный тестовый клиент
- `sample_package_data` - тестовые данные посылки

## 📊 Покрытие

Тесты покрывают:
- ✅ Валидацию входных данных
- ✅ API endpoints
- ✅ Бизнес-логику расчета стоимости
- ✅ Pydantic модели
- ✅ Обработку ошибок

## ⚠️ Примечания

- Тесты используют моки для внешних зависимостей
- Не требуют реальной базы данных
- Быстро выполняются (< 5 секунд)
- Поддерживают асинхронные тесты
