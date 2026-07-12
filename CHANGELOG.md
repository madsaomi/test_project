# СтудКарьера — Changelog

## Проект

Платформа для поиска стажировок в Узбекистане.
Стек: Django 5, DRF, ASGI (Daphne), Tailwind CSS, htmx, Alpine.js, Celery, PostgreSQL/SQLite.

## Сделано

### Архитектура
- Проект `studcareer/` с 8 приложениями: accounts, profiles, vacancies, applications, api, notifications, messaging, core
- ASGI-сервер (Daphne/Uvicorn), готовая асинхронная инфраструктура
- Docker Compose: web + db + redis + celery + celery-beat
- DRF API с JWT, permissions, throttling
- WebSockets (django-channels) для уведомлений
- Celery + eventlet для фоновых задач

### Модели
- `User` — кастомная модель (email as USERNAME_FIELD, role: student/employer)
- `StudentProfile` — город, желаемая должность, навыки, образование, опыт, языки, Telegram, LinkedIn, GitHub, портфолио
- `EmployerProfile` — компания, описание, логотип, сайт
- `Vacancy` + `Category` — вакансии с фильтрацией
- `Application` — отклики (unique_together, статусы: sent/viewed/invited/rejected)
- `Conversation` + `Message` — чат между студентом и работодателем

### Страницы
- `/` — главная с поиском, популярными направлениями, последними стажировками
- `/vacancies/` — каталог с фильтрацией (django-filter) и пагинацией
- `/vacancies/<id>/` — детальная страница вакансии с откликом
- `/accounts/signup/` — регистрация с выбором роли (студент/работодатель)
- `/accounts/login/` — вход (email + пароль, Google OAuth)
- `/dashboard/student/` — ЛК студента (профиль, отклики, статистика)
- `/dashboard/employer/` — ЛК работодателя (вакансии, отклики, статистика)
- `/dashboard/student/profile/` — форма редактирования профиля/резюме
- `/dashboard/employer/profile/` — форма редактирования компании
- `/applications/student/` — отклики студента
- `/applications/employer/<id>/` — отклики на вакансию (для работодателя)
- `/messages/` — чаты (inbox)
- `/messages/<id>/` — диалог
- `/api/` — DRF API (16 эндпоинтов)
- `/admin/` — Django Admin

### Дизайн
- SaaS-стиль: фиолетово-индиго градиент, скругления, тени
- Mobile First
- Все страницы allauth переопределены (login, signup, logout, reset password, etc.)
- Inline CSS (Tailwind CDN + fallback)
- Микроанимации на карточках и кнопках

### Аутентификация
- django-allauth (email + Google OAuth)
- Подтверждение email
- JWT для API (djangorestframework-simplejwt)
- django-axes (защита от брутфорса, 3 попытки → 15 мин блокировки)

### Чат
- Встроенный чат между студентом и работодателем
- Привязан к отклику (Application)
- Отметка о прочитанных сообщениях

### Данные
- `python manage.py seed_db` — заполнение тестовыми данными (10 студентов, 5 работодателей, 30 вакансий, 20 откликов)

## Тестовые аккаунты

```bash
Пароль: password123

Студенты:   student1@example.com … student10@example.com
Работодатели: employer1@example.com … employer5@example.com
Админ:      admin@admin.com / admin123
```

## Запуск

```bash
./run.sh --seed
# или
docker compose up -d
```
