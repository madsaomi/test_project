# StudCareer — AGENTS.md

Платформа поиска стажировок. Django 5, DRF, channels/ASGI, allauth, Celery, PostgreSQL/SQLite. Код и комментарии на русском. Требуется Python >=3.12.

## Команды

- Тесты: `pytest tests/ -v` (конфиг в `[tool.pytest.ini_options]`, `testpaths=["tests"]`, `DJANGO_SETTINGS_MODULE=config.settings`).
- Покрытие (CI падает ниже 60%): `coverage run -m pytest tests/ && coverage report --fail-under=60`.
- Lint: `ruff check .`; формат: `ruff format --check .` (line-length 100, кавычки двойные).
- Миграции: `python manage.py makemigrations`, `python manage.py migrate`. Проверка дрейфа: `makemigrations --check --dry-run`.
- Сидинг: `python manage.py seed_db` (данные + admin@admin.com; пароль генерится). См. `core/management/commands/seed_db.py`.
- pre-commit: `pre-commit install` (ruff --fix, ruff-format, mypy с django-stubs, mypy исключает tests/).

## Окружение (config/settings.py через environs, читает `.env`)

- `DJANGO_SECRET_KEY` — ОБЯЗАТЕЛЕН, дефолта нет; `DJANGO_DEBUG` по умолчанию `false`.
- `DATABASE_URL` — дефолт `sqlite:///db.sqlite3`; CI и docker-compose используют postgres.
- `REDIS_URL` — задан → redis-кэш, channels и celery; иначе locmem.
- **ГОТЧА system checks:** без Redis (locmem) `migrate`/`makemigrations` падают с `django_ratelimit.E003`; а django-csp>=4 даёт `csp.E001` (settings используют legacy `CSP_*`, работает только с `django-csp<4` — пин проекта). Локально добавляй `--skip-checks` к manage.py-командам.

## Архитектура

- `config/` — settings/asgi/wsgi/celery/urls; `ASGI_APPLICATION = config.asgi.application` (channels).
- Приложения: `accounts` (кастомный User), `profiles` (StudentProfile/EmployerProfile), `vacancies` (Vacancy/Category, фильтры в `vacancies/filters.py`), `applications` (Application), `messaging` (Conversation/Message), `notifications` (WebSocket-consumers), `api` (DRF + JWT + drf-spectacular), `core` (seed_db, templatetags).
- API: auth = simplejwt + Session; permissions в `api/permissions.py` (`IsStudent`, `IsEmployer`, `IsVacancyOwner`); throttle rates (`anon 30/min`, `user 120/min`, `apply 10/min`).
- Шаблоны: глобальный `templates/` + `templates/<app>/`; crispy-tailwind, htmx, Alpine.js, Tailwind c CDN (CSP разрешает `cdn.tailwindcss.com`).

## Модель User (accounts/models.py) — ключевое

- `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = ["role"]`, роли `student`/`employer`.
- Кастомный `UserManager` (`use_in_migrations=True`): `create_user(email, password=..., role=...)`, `create_superuser(...)` — **аргумент `username` НЕ принимается**.
- `username` генерится автоматически в `User.save()` (`{email_prefix}_{rand4}`).
- allauth: логин только по email, `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, адаптер `accounts.adapter.AccountAdapter`. В `AUTHENTICATION_BACKENDS` axes первый.

## Тестирование (tests/)

- `conftest.py`: фикстуры `api_client` (DRF `APIClient`), `student_user`/`employer_user` (через `create_user(email, ..., role=...)`), `student_profile`, `employer_profile`, `category`, `vacancy`, `application`.
- **ГОТЧА:** Django-вью (`tests/test_views.py`) аутентифицируют сессией — `client.force_login(user=...)`; API-вью (`test_api.py`, `test_permissions.py`) — `api_client.force_authenticate(user=...)`. Перепутать нельзя.
- `test_unique_together` (models): сначала создаётся отклик, потом `pytest.raises(Exception)` на дубликат (IntregrityError ловится во вью).

## История / текущее состояние

- Все 48 тестов проходят (`pytest tests/ -q`), `makemigrations --check` чистый.
- В этой сессии исправлены реальные баги — изменения **ЕЩЁ НЕ ЗАКОММИЧЕНЫ** (смотри `git status`):
  - `accounts/models.py`: добавлен `UserManager` — на Django 5.2 `create_user`/`create_superuser` падали без `username`.
  - Новые миграции: `accounts/0002_alter_user_managers`, `applications/0002_alter_application_unique_together_and_more` (`UniqueConstraint(vacancy, student)` вместо `unique_together` — блокирует дубли в БД), `messaging/0002_...` (db_index на `created_at`/`is_read`, `max_length=5000` у `text`).
  - Тесты: `test_views.py` переведены на `force_login`; `test_employer_cannot_create_application` ждёт 403, а не 400; `test_unique_together` создаёт первый отклик перед дубликатом.
  - Прочие: `api/views.py`, `api/permissions.py`, `messaging/views.py`, `vacancies/filters.py`, `seed_db.py`, `docker-compose.yml`.
- Локальная песочница (Termux, НЕ продакшен): Django стоит на python 3.13 (`/data/data/com.termux/files/usr/bin/python`); системный `python3` 3.14 без Django. `daphne` не ставится (нужна `cryptography` → Rust) — для локальных pytest-прогонов используется `/tmp/test_settings.py` (settings без daphne) с `DJANGO_SETTINGS_MODULE=test_settings` и `PYTHONPATH=/root/test_project:/tmp`. В Docker/CI ставится нормально.
- ИИ-интеграций/памяти для агентов в проекте нет.
