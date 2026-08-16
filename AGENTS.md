# StudCareer — AGENTS.md

Платформа поиска стажировок. Django 5, DRF, channels/ASGI, allauth, Celery, PostgreSQL/SQLite. Код и комментарии на русском. Требуется Python >=3.12.

**Роадмап, история изменений и правила ведения — в `docs/agents/` (начинай с `docs/agents/README.md`).**

## Команды

- Тесты: `pytest tests/ -v` (конфиг в `[tool.pytest.ini_options]`, `testpaths=["tests"]`, `DJANGO_SETTINGS_MODULE=config.settings`). Один тест: `pytest tests/test_views.py::TestDashboardRedirect::test_student_redirect`. Весь набор ~30-60 с (73 теста).
- Покрытие (CI падает ниже 60%): `coverage run -m pytest tests/ && coverage report --fail-under=60`. Порог и `source` в `[tool.coverage.*]` pyproject. Актуально ~82%.
- CI (`.github/workflows/ci.yml`): lint (`uvx ruff check` + format) → migrate → `check --deploy` → `makemigrations --check --dry-run` → pytest с покрытием → сборка Docker. Триггеры: push в main/develop, PR в main.
- Lint: `ruff check .`; формат: `ruff format --check .` (line-length 100, кавычки двойные).
- Миграции: `python manage.py makemigrations`, `python manage.py migrate`. Проверка дрейфа: `makemigrations --check --dry-run`.
- Сидинг: `python manage.py seed_db` (данные + admin@admin.com; пароль генерится). См. `core/management/commands/seed_db.py`.
- Зависимости: **единственный источник — `pyproject.toml`**; `requirements.txt` — сгенерированное зеркало `[project].dependencies` для удобства (`pip install -r requirements.txt`). CI ставит через `uv` (`uv venv .venv && uv pip install -e ".[dev]"`); Docker и `run.sh` — `pip install .` / `pip install -e ".[dev]"`. SMTP-настройки (`EMAIL_HOST`, `EMAIL_*`) — через анвирон, дефолт console.
- pre-commit: `pre-commit install` (ruff --fix, ruff-format, mypy с django-stubs, mypy исключает tests/).
- Tailwind (обязательно после правки шаблонов): `/root/.local/bin/tailwind -i static/css/input.css -o static/css/app.css --minify` — standalone v3.4, контент-скан в `tailwind.config.js` (`content: ["./templates/**/*.html"]`). Кастомные классы (`card-gradient`, `mesh-pattern`, `skeleton`, body-фон) — в `input.css`.
- Git: conventional commits (`feat:`, `fix:`, `test:`, `docs:`), история по-английски.

## Окружение (config/settings.py через environs, читает `.env`)

- `DJANGO_SECRET_KEY` — ОБЯЗАТЕЛЕН, дефолта нет; `DJANGO_DEBUG` по умолчанию `false`.
- `DATABASE_URL` — дефолт `sqlite:///db.sqlite3`; CI и docker-compose используют postgres.
- `REDIS_URL` — задан → redis-кэш, channels и celery; иначе locmem.
- **ГОТЧА system checks:** без Redis (locmem) `migrate`/`makemigrations` падают с `django_ratelimit.E003`. Локально добавляй `--skip-checks` к manage.py-командам.
- Celery: `core/tasks.py` — задачи email-уведомлений (`send_new_application_email`, `send_new_message_email`). Без `REDIS_URL` включён eager-режим (`CELERY_TASK_ALWAYS_EAGER`) — задачи выполняются синхронно, в тестах почта идёт в outbox.

## Архитектура

- `config/` — settings/asgi/wsgi/celery/urls; `ASGI_APPLICATION = config.asgi.application` (channels).
- Приложения: `accounts` (кастомный User), `profiles` (StudentProfile/EmployerProfile), `vacancies` (Vacancy/Category, фильтры в `vacancies/filters.py`), `applications` (Application), `messaging` (Conversation/Message), `notifications` (WebSocket-consumers), `api` (DRF + JWT + drf-spectacular), `core` (seed_db, templatetags).
- API: auth = simplejwt + Session; permissions в `api/permissions.py` (`IsStudent`, `IsEmployer`, `IsVacancyOwner`); throttle rates (`anon 30/min`, `user 120/min`, `apply 10/min`).
- Шаблоны: глобальный `templates/` + `templates/<app>/`; crispy-tailwind, htmx, Alpine.js. Tailwind — **собранная статика** `static/css/app.css` (без CDN-скрипта); Google Fonts через `<link>`. CSP (django-csp 4, формат `CONTENT_SECURITY_POLICY`): `unsafe-inline` только в style-src (Alpine-переходы), в script-src нет.

## Модель User (accounts/models.py) — ключевое

- `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = ["role"]`, роли `student`/`employer`.
- Кастомный `UserManager` (`use_in_migrations=True`): `create_user(email, password=..., role=...)`, `create_superuser(...)` — **аргумент `username` НЕ принимается**.
- `username` генерится автоматически в `User.save()` (`{email_prefix}_{rand4}`).
- allauth: логин только по email, `ACCOUNT_EMAIL_VERIFICATION = "none"` (верификация отключена), адаптер `accounts.adapter.AccountAdapter`. В `AUTHENTICATION_BACKENDS` axes первый.

## Тестирование (tests/)

- `conftest.py`: фикстуры `api_client` (DRF `APIClient`), `student_user`/`employer_user` (через `create_user(email, ..., role=...)`), `student_profile`, `employer_profile`, `category`, `vacancy`, `application`.
- **ГОТЧА:** Django-вью (`tests/test_views.py`) аутентифицируют сессией — `client.force_login(user=...)`; API-вью (`test_api.py`, `test_permissions.py`) — `api_client.force_authenticate(user=...)`. Перепутать нельзя.
- `test_unique_together` (models): сначала создаётся отклик, потом `pytest.raises(Exception)` на дубликат (IntregrityError ловится во вью).
- `test_messaging.py` (13) / `test_notifications.py` (4 async, `WebsocketCommunicator`): закрыли messaging и consumers. Готча: websocket-тестам нужен `CHANNEL_LAYERS` без Redis (InMemory задаётся в `config/settings.py` при пустом `REDIS_URL`; в тестах можно override).

## История / текущее состояние

- **main = `5c12bb5`** (рабочее дерево после сессии 2026-08-10). Локально ветка ушла вперёд от
  `origin/main` на 7+ незапушенных коммитов. **73 теста проходят** (`pytest tests/ -q`),
  `makemigrations --check` чистый, покрытие **~82%**.
- Недавняя история: `5c12bb5` CV-загрузка, `33c6d98` полнотекстовый поиск, `36483ad` Celery email,
  `e286d66` пины+CSP, `6ce1892` бенчмарк, `3693b87` Tailwind-сборка, `430ad96` тестовый набор, `1ee7774` тесты (40+).
- Сессия 2026-08-10 (НЕ закоммичено): SMTP-настройки, `check --deploy`+drift-проверка в CI,
  переход на uv/удаление `requirements.txt`, тесты `messaging` (13) и `notifications` (4),
  фикс коммуникаций (`messaging/views.py` — не было `return` в `get_queryset`), `CHANNEL_LAYERS`
  на InMemory без Redis, изоляция `MEDIA_ROOT` в тестах. Покрытие 76% → 82%.
- В прошлой сессии исправлены реальные баги (всё в `430ad96`):
  - `accounts/models.py`: добавлен `UserManager` — на Django 5.2 `create_user`/`create_superuser` падали без `username`.
  - Новые миграции: `accounts/0002_alter_user_managers`, `applications/0002_alter_application_unique_together_and_more` (`UniqueConstraint(vacancy, student)` вместо `unique_together` — блокирует дубли в БД), `messaging/0002_...` (db_index на `created_at`/`is_read`, `max_length=5000` у `text`).
  - Тесты: `test_views.py` переведены на `force_login`; `test_employer_cannot_create_application` ждёт 403, а не 400; `test_unique_together` создаёт первый отклик перед дубликатом.
  - Прочие: `api/views.py`, `api/permissions.py`, `messaging/views.py`, `vacancies/filters.py`, `seed_db.py`, `docker-compose.yml`.
- Локальная песочница (Termux, НЕ продакшен): Django стоит на python 3.13 (`/data/data/com.termux/files/usr/bin/python`); системный `python3` 3.14 без Django. `daphne` не ставится (нужна `cryptography` → Rust) — для локальных pytest-прогонов используется `/tmp/test_settings.py` (settings без daphne):
  ```
  DJANGO_SECRET_KEY=test DJANGO_DEBUG=false DJANGO_SETTINGS_MODULE=test_settings PYTHONPATH=/root/test_project:/tmp python -m pytest tests/ -v
  ```
  В Docker/CI ставится нормально.
- ИИ-интеграций/памяти для агентов в проекте нет.
