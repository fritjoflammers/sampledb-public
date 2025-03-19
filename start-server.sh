#!/usr/bin/env bash
# start-server.sh

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd sampledb; python manage.py createsuperuser --no-input)
fi
( gunicorn sampledb.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "user www-data www-data;" #-g "daemon off;"