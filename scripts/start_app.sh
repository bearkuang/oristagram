#!/bin/bash
docker run -d --name origram -p 8000:8000 \
  -e DB_NAME=${DB_NAME} \
  -e DB_USER=${DB_USER} \
  -e DB_PASSWORD=${DB_PASSWORD} \
  -e DB_HOST=${DB_HOST} \
  my-django-app

docker exec origram python manage.py migrate
