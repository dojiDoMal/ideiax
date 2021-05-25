#!/bin/bash

LOG_LEVEL=${LOG_LEVEL:-"info"}

cd /app

export DJANGO_SETTINGS_MODULE=ideax.settings.dev
pip install -r /app/requirements/dev.txt

python manage.py collectstatic --no-input

# TODO: Encontrar método melhor de aguardar o banco de dados
sleep 5

python manage.py migrate
python manage.py compilemessages

if [ ! -f /provisioned ]; then
  echo "First time setup"
  python manage.py loaddata docker/initialdata.json
  touch /provisioned
fi

while true; do
    ./manage.py runserver 0.0.0.0:8000
    # ./manage.py runserver_plus 0.0.0.0:8000
    echo "Re-starting Django runserver in 5 seconds..."
    sleep 5
done

# exec gunicorn ideax.wsgi:application \
#     --name ideax_django \
#     --bind 0.0.0.0:8000 \
#     --workers 5 \
#     --log-level=${LOG_LEVEL} \
# "$@"
