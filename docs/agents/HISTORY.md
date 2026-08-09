# История изменений

Хронология по коммитам и сессиям. Добавляй новый блок сверху в раздел «Сессии».

## Сессии

### 2026-08-09 — frontend: настоящая сборка Tailwind вместо CDN

**Сделано:**
- `tailwind.config.js`: контент-скан `templates/**/*.html`, кастомные шрифты (Plus Jakarta Sans, JetBrains Mono), тени `shadow-teal`/`shadow-amber`.
- `static/css/input.css` стал живым источником: кастомные классы `card-gradient`, `mesh-pattern`, `skeleton` + `prefers-reduced-motion` перенесены из `<style>` в input.css.
- `static/css/app.css` — сгенерированный минифицированный CSS (27 КБ).
- `templates/base.html`: убран `<script src="cdn.tailwindcss.com">` и весь ручной `<style>`-блок (444 строки); подключён `{% static 'css/app.css' %}`.
- `config/settings.py`: из CSP script-src убраны `cdn.tailwindcss.com` и `'unsafe-inline'` (inline-скриптов в шаблонах нет); `unsafe-inline` оставлен в style-src (нужен Alpine-переходам).

**Результат:** все страницы рендерятся с app.css, `cdn.tailwindcss.com` нигде не остался, 48 тестов зелёные.

### 2026-08-09 — восстановление тестового набора на Django 5.2

**Проблема:** репозиторий обещал «40+ тестов», но тесты не запускались вообще
(окружение не было настроено). После установки зависимостей на Django 5.2.17 вскрылись
реальные баги.

**Сделано:**
- `accounts/models.py`: добавлен `UserManager` — на Django 5.2 `create_user`/`create_superuser`
  падали без аргумента `username` (всё в коде и тестах зовёт их по email). username
  генерится в `User.save()`.
- Миграции (в БД их не хватало, модель была «впереди» миграций):
  - `accounts/0002_alter_user_managers` — новый менеджер;
  - `applications/0002_alter_application_unique_together_and_more` — `UniqueConstraint(vacancy, student)`
    вместо `unique_together` (дубли откликов не блокировались на уровне БД);
  - `messaging/0002_...` — `db_index` на `created_at`/`is_read`, `max_length=5000` у `text`.
- Тесты: `test_views.py` переведены на `force_login` (сессия) вместо `force_authenticate` (DRF);
  `test_employer_cannot_create_application` ждёт 403 (не 400); `test_unique_together` создаёт
  первый отклик перед дубликатом.
- Прочие фиксы: `api/views.py`, `api/permissions.py`, `messaging/views.py`, `vacancies/filters.py`,
  `core/management/commands/seed_db.py`, `docker-compose.yml`.
- Добавлен корневой `AGENTS.md` и этот каталог `docs/agents/`.

**Результат:** `pytest tests/ -q` — 48 passed, `makemigrations --check` чистый.
Закоммичено как `430ad96` и запушено в `main`.

**Окружение (локальная песочница):** Django на Termux-python 3.13; `daphne` не ставится
(нужна `cryptography` → Rust), поэтому локально тесты гоняются через `/tmp/test_settings.py`
(settings без daphne). См. команду в `AGENTS.md`.

## Коммиты (main)

| Коммит | Тип | Суть |
|--------|-----|------|
| `430ad96` | fix | enable test suite on Django 5.2 — UserManager, миграции, фиксы тестов, AGENTS.md |
| `1ee7774` | test | comprehensive test suite — 40+ тестов (models, API, views, permissions) |
| `6c59fed` | feat | редизайн фронтенда: teal-палитра, Plus Jakarta Sans, mesh-паттерн, обновлены все 30 шаблонов |
| `13b86bd` | fix | бэкенд: N+1, пропущенные индексы, deprecated API, ошибки |
| `5ff507a` | feat | CI/CD и инструменты: GitHub Actions, pre-commit, ruff, mypy, sentry-sdk |
| `d8c5b4c` | feat | Docker: multi-stage, nginx, Redis auth, healthchecks, non-root |
| `30b35d3` | feat | API: delete, ordering, Swagger docs, IDOR fix |
| `f28b413` | fix | security: SECRET_KEY обязателен, DEBUG=false, CSP, admin-пароль |
| `2e20cc9` | — | first commit |
