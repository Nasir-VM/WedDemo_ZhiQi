#!/bin/sh
set -eu

umask 027

: "${SQLITE_PATH:=/data/db.sqlite3}"
: "${MEDIA_ROOT:=/data/media}"
: "${BACKUP_DIR:=/data/backups}"

mkdir -p "$(dirname "$SQLITE_PATH")" "$MEDIA_ROOT" "$BACKUP_DIR"

python manage.py migrate --noinput

if [ -n "${DJANGO_ADMIN_PASSWORD:-}" ]; then
    python manage.py ensure_admin
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-3}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --capture-output
