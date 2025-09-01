# 🚚 Dostavka API

API для системы доставки посылок с автоматическим расчетом стоимости доставки, пагинацией и фильтрацией.

## 🏗️ Архитектура

- **FastAPI** - веб-фреймворк для API
- **PostgreSQL** - основная база данных
- **Redis** - кеширование курсов валют
- **RabbitMQ** - очередь сообщений
- **Celery** - асинхронные задачи
- **Docker & Docker Compose** - контейнеризация

## ✨ Основные возможности

- Создание посылок с автоматическим расчетом стоимости доставки
- Управление посылками с пагинацией и фильтрацией
- Асинхронная обработка через Celery и RabbitMQ
- Кеширование курсов валют в Redis
- Автоматический расчет стоимости доставки на основе веса и цены
- Использование актуального курса USD/RUB от ЦБ РФ

## 🚀 Быстрый старт

### Предварительные требования

- Docker
- Docker Compose

### Запуск проекта

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd dostavka
```

2. **Запустите все сервисы:**
```bash
docker-compose -f docker-compose-local.yaml up -d
```

3. **Проверьте статус сервисов:**
```bash
docker-compose -f docker-compose-local.yaml ps
```

4. **Откройте Swagger UI:**
```
http://localhost:8000/docs
```

### Остановка проекта

```bash
docker-compose -f docker-compose-local.yaml down
```

### Просмотр логов

```bash
# Все сервисы
docker-compose -f docker-compose-local.yaml logs -f

# Конкретный сервис
docker-compose -f docker-compose-local.yaml logs -f app
docker-compose -f docker-compose-local.yaml logs -f celery
docker-compose -f docker-compose-local.yaml logs -f db
```

## 📚 API Документация

### Базовый URL
```
http://localhost:8000
```

### Аутентификация
API использует сессионную аутентификацию через middleware. При первом запросе автоматически создается сессия.

### Эндпоинты

#### 1. Создание посылки
```http
POST /packages/
```

**Описание:** Создает новую посылку и отправляет задачу в Celery для расчета стоимости доставки.

**Тело запроса:**
```json
{
    "name": "iPhone 15 Pro",
    "weight": 0.2,
    "type_id": 1,
    "price": 89990.0
}
```

**Ответ:**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing"
}
```

**Процесс:**
1. Создается запись в базе данных
2. Задача отправляется в RabbitMQ
3. Celery worker рассчитывает стоимость доставки
4. База данных обновляется с рассчитанной стоимостью

#### 2. Получение посылок с пагинацией
```http
GET /packages/?page=1&size=10&type_id=1&has_shipping_cost=true
```

**Параметры запроса:**
- `page` (int, по умолчанию: 1) - номер страницы (начиная с 1)
- `size` (int, по умолчанию: 10, макс: 100) - размер страницы
- `type_id` (int, опционально) - фильтр по типу посылки
- `has_shipping_cost` (bool, опционально) - фильтр по наличию рассчитанной стоимости

**Примеры запросов:**
```bash
# Базовая пагинация
GET /packages/?page=1&size=10

# Фильтр по типу
GET /packages/?type_id=1&page=1&size=20

# Фильтр по стоимости доставки
GET /packages/?has_shipping_cost=true&page=1&size=15

# Комбинированные фильтры
GET /packages/?type_id=2&has_shipping_cost=false&page=2&size=25
```

**Ответ:**
```json
{
    "packages": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "iPhone 15",
            "weight": 0.2,
            "type_id": 1,
            "price": 89990.0,
            "shipping_cost": "1349.85",
            "session_id": "session-uuid"
        }
    ],
    "total": 25,
    "page": 1,
    "size": 10,
    "pages": 3
}
```

#### 3. Получение типов посылок
```http
GET /packages/types
```

**Описание:** Возвращает список всех доступных типов посылок.

**Ответ:**
```json
[
    {
        "id": 1,
        "name": "Электроника"
    },
    {
        "id": 2,
        "name": "Одежда"
    }
]
```

#### 4. Получение информации о посылке
```http
GET /packages/{package_id}
```

**Описание:** Возвращает детальную информацию о конкретной посылке.

**Ответ:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "iPhone 15",
    "weight": 0.2,
    "type_id": 1,
    "price": 89990.0,
    "shipping_cost": "1349.85"
}
```

## 🔧 Конфигурация

### Переменные окружения

Основные настройки находятся в `src/dostavka/settings.py`:

- `REAL_DATABASE_URL` - URL базы данных PostgreSQL
- `REDIS_URL` - URL Redis сервера
- `RABBITMQ_URL` - URL RabbitMQ сервера

### Порты

- **FastAPI**: 8000
- **PostgreSQL**: 5432
- **Redis**: 6379
- **RabbitMQ**: 5672
- **RabbitMQ Management**: 15672

## 📊 Расчет стоимости доставки

### Формула
```
Стоимость доставки = ((Вес × 0.5) + (Цена × 0.01)) × Курс USD/RUB
```

### Процесс
1. При создании посылки `shipping_cost` устанавливается как "Не рассчитано"
2. Задача отправляется в Celery через RabbitMQ
3. Celery worker получает актуальный курс USD/RUB из Redis
4. Рассчитывается стоимость доставки
5. База данных обновляется с рассчитанной стоимостью

## 🚨 Обработка ошибок

API использует стандартизированные HTTPException с детальной информацией об ошибках:

### Формат ошибки
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Описание ошибки",
        "details": {
            "additional_info": "value"
        }
    }
}
```

### Коды ошибок
- `VALIDATION_ERROR` (422) - ошибка валидации данных
- `NOT_FOUND` (404) - ресурс не найден
- `FORBIDDEN` (403) - доступ запрещен
- `CONFLICT` (409) - конфликт данных
- `INTERNAL_SERVER_ERROR` (500) - внутренняя ошибка сервера

## 🧪 Тестирование

### Автоматические тесты

Проект включает набор автоматических тестов для проверки функциональности:

```bash
# Запустить все тесты
make test

# Тесты с подробным выводом
make test-verbose

# Тесты с покрытием кода
make test-coverage
```

### Swagger UI
Откройте `http://localhost:8000/docs` для интерактивного тестирования API.

### Примеры запросов

**Создание посылки:**
```bash
curl -X POST "http://localhost:8000/packages/" \
     -H "Content-Type: application/json" \
     -d '{
         "name": "MacBook Pro",
         "weight": 2.1,
         "type_id": 1,
         "price": 199990.0
     }'
```

**Получение посылок:**
```bash
curl "http://localhost:8000/packages/?page=1&size=5"
```

**Получение типов:**
```bash
curl "http://localhost:8000/packages/types"
```

## 🔍 Мониторинг

### Логи Celery
```bash
docker-compose -f docker-compose-local.yaml logs -f celery
```

### Логи приложения
```bash
docker-compose -f docker-compose-local.yaml logs -f app
```

### Статус сервисов
```bash
docker-compose -f docker-compose-local.yaml ps
```

## 🛠️ Разработка

### Требования для разработки

- Python 3.9+
- Poetry
- Docker & Docker Compose
- Make (опционально)

### Установка зависимостей

```bash
# Основные зависимости
poetry install --only=main

# Все зависимости (включая dev)
poetry install
pre-commit install
```

### Качество кода

Проект использует современные инструменты для поддержания качества кода:

- **Ruff** - быстрый линтер Python
- **Black** - автоматический форматировщик
- **isort** - сортировка импортов
- **Pre-commit** - автоматические проверки при коммите

```bash
# Форматировать код
make format

# Проверить качество
make lint

# Все проверки
make check-all
```

### Структура проекта
```
src/dostavka/
├── api/           # API эндпоинты и модели
├── celery/        # Celery задачи и конфигурация
├── core/          # Основной функционал (логирование)
├── db/            # База данных, модели и DAL
├── redis/         # Redis кеш
├── services/      # Бизнес-логика
└── main.py        # Точка входа приложения
```

### Добавление новых эндпоинтов
1. Создайте функцию в `src/dostavka/api/handlers.py`
2. Добавьте роут с декоратором `@package_router.xxx()`
3. Добавьте обработку ошибок через `HTTPException`
4. Обновите документацию

### Добавление новых моделей
1. Создайте модель в `src/dostavka/db/models.py`
2. Добавьте методы в соответствующий DAL класс
3. Создайте Pydantic модели в `src/dostavka/api/models.py`

### Подробное руководство

См. файл [DEVELOPMENT.md](DEVELOPMENT.md) для детального руководства по разработке.

