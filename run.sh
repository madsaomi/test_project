#!/usr/bin/env bash
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

RED='\033[1;31m'; GREEN='\033[1;32m'; CYAN='\033[1;36m'; NC='\033[0m'
step() { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }
ok()  { echo -e "${GREEN}✓ $1${NC}"; }
fail(){ echo -e "${RED}✗ $1${NC}"; exit 1; }

[ ! -f ".env" ] && cp .env.example .env && python3 -c "
import secrets
with open('.env', 'r') as f:
    content = f.read()
if 'DJANGO_SECRET_KEY=' in content:
    content = content.replace('DJANGO_SECRET_KEY=change-me-to-a-random-secret-key',
                              f'DJANGO_SECRET_KEY={secrets.token_urlsafe(50)}')
if 'REDIS_PASSWORD=' in content:
    content = content.replace('REDIS_PASSWORD=changeme',
                              f'REDIS_PASSWORD={secrets.token_urlsafe(16)}')
with open('.env', 'w') as f:
    f.write(content)
"

if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    step "Docker режим"
    docker compose up -d --build
    until docker compose exec db pg_isready -U postgres -d studcareer &>/dev/null 2>&1; do sleep 1; done
    docker compose exec web python manage.py migrate --noinput
    [ "$1" = "--seed" ] && docker compose exec web python manage.py seed_db
    docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model; User=get_user_model()
import secrets
if not User.objects.filter(is_superuser=True).exists():
    admin_pass = secrets.token_urlsafe(16)
    User.objects.create_superuser(email='admin@admin.com', password=admin_pass, role='employer')
    print(f'admin: admin@admin.com / {admin_pass}')
"
    echo -e "\n${GREEN}━━━ СтудКарьера запущена! ━━━${NC}"
    echo -e "  Сайт:    http://localhost:80"
    echo -e "  Админка: http://localhost:80/admin/"
    echo -e "  API:     http://localhost:80/api/"
    echo -e "  API Docs: http://localhost:80/api/docs/"
    exit 0
fi

step "Локальный запуск"

OS="$(uname -s)"
case "$OS" in
    Linux*)   ACTIVATE="venv/bin/activate" ;;
    Darwin*)  ACTIVATE="venv/bin/activate" ;;
    MINGW*|MSYS*|CYGWIN*) ACTIVATE="venv/Scripts/activate" ;;
    *)        ACTIVATE="venv/bin/activate" ;;
esac

if [ ! -d "venv" ]; then
    python3 -m venv venv && ok "venv создан"
fi
source "$ACTIVATE"

step "Установка зависимостей"
pip install --upgrade pip setuptools wheel --quiet
# Единственный источник зависимостей — pyproject.toml
if ! pip install -e ".[dev]"; then
    echo -e "${RED}Не удалось установить зависимости из pyproject.toml${NC}"
    exit 1
fi

step "Миграции"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

[ "$1" = "--seed" ] && python manage.py seed_db

python manage.py shell -c "
from django.contrib.auth import get_user_model; User=get_user_model()
import secrets
if not User.objects.filter(is_superuser=True).exists():
    admin_pass = secrets.token_urlsafe(16)
    User.objects.create_superuser(email='admin@admin.com', password=admin_pass, role='employer')
    print(f'admin: admin@admin.com / {admin_pass}')
" 2>/dev/null || true

echo -e "\n${GREEN}━━━ Запуск сервера ━━━${NC}"
echo -e "  http://127.0.0.1:8000\n"
export DJANGO_DEBUG=true
python manage.py runserver
