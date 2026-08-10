# Роадмап

План развития StudCareer. Обновляй при изменении приоритетов. Легенда статусов:
`[x]` — сделано, `[~]` — в работе, `[ ]` — запланировано.

Приоритеты основаны на сравнении с аналогами (PeelJobs/opensource-job-portal и др.)
и рекомендациями по Django-стеку на 2026 г. Исследование — см. `HISTORY.md` (сессия 2026-08-09, бенчмарк).

## Приоритет 1 — ядро платформы

- `[x]` **Полнотекстовый поиск вакансий**: PostgreSQL — `SearchVector`/`SearchRank`
  по title/description/requirements/conditions/city с ранжированием; SQLite — OR по `icontains`
  (`vacancies/filters.py`, работает и в web, и в API). Без схемных миграций (портативно).
- `[x]` **Обновить устаревшие пины** (проверено по PyPI):
  - `djangorestframework`: пин `<3.16`, актуально 3.18 → теперь `<3.19`;
  - `django-filter`: пин `<25`, актуально 26.1 → теперь `<27`;
  - `django-csp`: legacy `CSP_*` → `CONTENT_SECURITY_POLICY`, пин `<4` → `<5` (установлен 4.0).
- `[x]` **Первые Celery-задачи + email-уведомления** по событиям (новый отклик/сообщение):
  `core/tasks.py` (`send_new_application_email`, `send_new_message_email`), привязаны во вью
  `ApplyToVacancyView` и `SendMessageView`; без Redis — eager-режим. 52 теста.
- `[x]` **Загрузка резюме/CV** студентом: поле `StudentProfile.resume` уже было в модели
  и показывалось работодателю в откликах; добавлено в `StudentProfileForm` и шаблон
  (`enctype=multipart/form-data`, индикатор загруженного файла).

## Приоритет 2 — довести до продакшена

- `[x]` **SMTP-бэкенд**: `EMAIL_BACKEND`/`EMAIL_HOST`/`EMAIL_*` через environs,
  default — console (dev/тесты); без SMTP проде не обойтись при `mandatory`-верификации.
- `[x]` `python manage.py check --deploy` добавлен в CI (+ `makemigrations --check --dry-run`).
- `[x]` Консолидировать зависимости: `requirements.txt` удалён, единственный источник —
  `pyproject.toml`, CI переведён на `uv` (Docker/`run.sh` — pip из pyproject).
- `[ ]` HTTPS/TLS на nginx (сейчас `SECURE_SSL_REDIRECT=false` и нет certbot).
- `[ ]` Модульные settings (base/local/production) вместо одного `settings.py`.
- `[ ]` i18n/l10n: сейчас только русский, без `locale/` (аудитория — Узбекистан).

## Ближние задачи

- `[x]` Включить полноценный тестовый набор (73 теста, Django 5.2).
- `[x]` Покрытие **82%** — порог 60% в CI проходит (`coverage report --fail-under=60`).
- `[x]` Тесты для `messaging` (диалоги, отметки прочитанного) — 13 тестов;
  попутно исправлен баг в `InboxView.get_queryset` (не было `return`).
- `[x]` Тесты для `notifications` (WebSocket consumers) — 4 async-теста.
- `[ ]` Тесты авторизации (allauth-потоки: регистрация, подтверждение email, Google OAuth).

## Функциональные задачи

- `[ ]` Отправка уведомлений по событиям (новый отклик, новое сообщение) —
  потребители в `notifications/consumers.py` есть, но событий нет
  (события можно слать в WebSocket-группу `user_{id}` через Celery-задачи).
- `[ ]` Проверить email-потоки при `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`
  (SMTP-настройки добавлены, нужен реальный бэкенд в проде).
- `[ ]` Employer-сценарий по вакансиям: полный CRUD через UI и API-эквиваленты.

## Инфраструктура / качество

- `[x]` Настоящая сборка Tailwind: standalone CLI → `static/css/app.css`, убран CDN-скрипт
  и `unsafe-inline` из script-src в CSP.
- `[ ]` Поднять `mypy` (pre-commit) — проверять чистоту, т.к. hooks настроены.
- `[ ]` Актуализировать `CHANGELOG.md` (сейчас не отражает изменения после `6c59fed`).
- `[ ]` Покрыть CI для develop-ветки (deploy-сценарий, если нужен).

## Заметки

- Проект поддерживает async (channels/ASGI), но тесты синхронные — pytest-asyncio
  установлен, если понадобятся async-тесты.
- Код и комментарии — на русском, коммиты — на английском (conventional commits).
