#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

if [ "$DOCKER_APP_ENVIRONMENT" = "DEV" ]
then
  echo "Executing migrations and collectstatic"
  python manage.py migrate --noinput
  python manage.py collectstatic --no-input
fi

exec "$@"
