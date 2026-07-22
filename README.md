# StudCareer

Платформа для поиска стажировок в Узбекистане.

**Стек:** Django 5, DRF, ASGI, PostgreSQL, Tailwind CSS, htmx, Alpine.js, Celery, Docker, Nginx

## Быстрый старт

```bash
cp .env.example .env
# Отредактируйте .env (задайте SECRET_KEY, пароли БД/Redis)
./run.sh --seed
```

Открой http://localhost:8000

## Docker

```bash
docker compose up -d
```

Сайт доступен на http://localhost:80

## Тестовые аккаунты

```
Студенты:       student1@example.com … student10@example.com
Работодатели:   employer1@example.com … employer5@example.com
Пароль:         password123

Админ:          admin@admin.com (пароль генерируется автоматически при запуске)
```

## API

Документация API: http://localhost:8000/api/docs/
Schema (OpenAPI): http://localhost:8000/api/schema/

## Development

```bash
# Установка pre-commit hooks
pre-commit install

# Linting
ruff check .
ruff format .

# Тесты
pytest tests/ -v
coverage run -m pytest tests/
coverage report
```

## Структура проекта

```
├── accounts/       # Аутентификация, пользователи
├── profiles/       # Профили студентов и работодателей
├── vacancies/      # Вакансии и категории
├── applications/   # Отклики на вакансии
├── messaging/      # Чат между студентами и работодателями
├── notifications/  # WebSocket уведомления
├── api/            # REST API (DRF)
├── core/           # Общие шаблонные теги
├── config/         # Настройки Django
├── nginx/          # Конфигурация Nginx
├── tests/          # Тесты
└── .github/        # CI/CD
```

## Environment Variables

См. `.env.example` для полного списка переменных.
