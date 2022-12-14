#!/usr/bin/env bash

#Change to service user and install + update virtual python environment
sudo su - ip2tor
cd /home/ip2tor/ip2tor
role=${CONTAINER_ROLE:-django-daphne}

# This is where the global python packages are installed
# python3 -m site

if [ "$role" = "django-http" ]; then
  echo "App role (Django HTTP server) ..."

  # Load the env variables from the root folder into the django .env file
  source /home/ip2tor/.env
  if [ ! -f "/home/ip2tor/ip2tor/.env" ]; then
    touch .env
    echo -e 'DEBUG=false' | tee --append .env
    # add the database URL, email URL and admin data from the root .env file
    echo -e 'DATABASE_URL="'$DATABASE_URL'"' | tee --append .env
    echo -e 'EMAIL_URL="'$EMAIL_URL'"' | tee --append .env
    # add the secret key
    python3 /home/ip2tor/.docker/get-secret-key.py | tee --append .env
  fi

  mkdir /home/ip2tor/media
  mkdir /home/ip2tor/static

  # Run django setup jobs
  python3 manage.py collectstatic <<<yes # confirm overwrite if the folder already contains files
  python3 manage.py makemigrations  # should normally not create new migrations!
  python3 manage.py migrate
  python3 manage.py createsuperuser_programatically --user=$DJANGO_SUPERUSER_NAME --password=$DJANGO_SUPERUSER_PASSWORD --email=$DJANGO_SUPERUSER_EMAIL

  # Limit access rights to base and media directory
  # chmod 700 /home/ip2tor/ip2tor  # !!! uncomment after debugging
  
  # Leaving r-x in Other for both folders
  chmod -R 755 /home/ip2tor/media 
  chmod -R 755 /home/ip2tor/static

  echo "Starting Django HTTP server in port "$DJANGO_HTTP_PORT"... "
  # python3 manage.py runserver 0.0.0.0:$DJANGO_HTTP_PORT
  gunicorn --bind=0.0.0.0:$DJANGO_HTTP_PORT django_ip2tor.wsgi
  
elif [ "$role" = "django-daphne" ]; then
  source /home/ip2tor/.env
  echo "App role (Django Daphne server) ..."
  echo "Starting Django with Daphne in port "$DJANGO_DAPHNE_PORT"... "
  
  # /home/ip2tor/venv/bin/daphne -b 0.0.0.0 -p $DJANGO_DAPHNE_PORT --proxy-headers django_ip2tor.asgi:application
  daphne -b 0.0.0.0 -p $DJANGO_DAPHNE_PORT --proxy-headers django_ip2tor.asgi:application

elif [ "$role" = "celery-beat" ] || [ "$role" = "celery-worker" ] || [ "$role" = "celery-flower" ]; then
  echo "Celery roles ..."

# cat <<EOF | sudo tee "/etc/tmpfiles.d/ip2tor.conf" >/dev/null
# d /run/ip2tor 0755 ip2tor ip2tor -
# d /var/log/ip2tor 0755 ip2tor ip2tor -
# EOF
# sudo systemd-tmpfiles --create --remove

  sudo install -m 0644 -o root -g root -t /etc/ /home/ip2tor/ip2tor/contrib/ip2tor-celery.conf
  source /etc/ip2tor-celery.conf

  if [ "$role" = "celery-worker" ]; then
    echo "Starting Celery worker ..."

    

    # safety switch, exit script if there's error. Full command of shortcut `set -e`
    set -o errexit
    # safety switch, uninitialized variables will stop script. Full command of shortcut `set -u`
    set -o nounset

    # tear down function
    teardown()
    {
        echo " Signal caught..."
        echo "Stopping celery multi gracefully..."

        # send shutdown signal to celery workser via `celery multi`
        # command must mirror some of `celery multi start` arguments
        ${CELERY_BIN} multi stop ${CELERYD_NODES}  \
          -A ${CELERY_APP} \
          --logfile=${CELERYD_LOG_FILE} \
          --loglevel=${CELERYD_LOG_LEVEL} \
          ${CELERYD_OPTS}

        echo "Stopped celery multi..."
        echo "Stopping last waited process"
        kill -s TERM "$child" 2> /dev/null
        echo "Stopped last waited process. Exiting..."
        exit 1
    }

    # start celery worker via `celery multi` with declared logfile for `tail -f`
    ${CELERY_BIN} multi start ${CELERYD_NODES}  \
      -A ${CELERY_APP} \
      --logfile=${CELERYD_LOG_FILE} \
      --loglevel=${CELERYD_LOG_LEVEL} \
      ${CELERYD_OPTS}
    # Pid  and Log files are created by default in the folder where we run celery
    # --pidfile=${CELERYD_PID_FILE} \

    # start trapping signals (docker sends `SIGTERM` for shudown)
    trap teardown SIGINT SIGTERM

    # tail all the logs continuously to console for `docker logs` to see
    tail -f ${CELERYD_LOG_FILE} &

    # capture process id of `tail` for tear down
    child=$!

    # waits for `tail -f` indefinitely and allows external signals,
    # including docker stop signals, to be captured by `trap`
    wait "$child"

  elif [ "$role" = "celery-flower" ]; then
    echo "Starting Celery flower ..."
    ${CELERY_BIN} -A ${CELERY_APP} flower
  fi

#   if [ "$role" = "celery-beat" ]; then
#     echo "Starting Celery beat ..."
#     ${CELERY_BIN} -A ${CELERY_APP} beat  \
#     --pidfile=${CELERYBEAT_PID_FILE} \
#     -s ${CELERYBEAT_SCHEDULE_FILE} \
#     --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} \
#     --scheduler django_celery_beat.schedulers:DatabaseScheduler



else
    echo "Could not match the container role \"$role\""
    exit 1
fi

# unset POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB DATABASE_URL EMAIL_URL ADMIN_NAME ADMIN_EMAIL DJANGO_SUPERUSER_NAME DJANGO_SUPERUSER_PASSWORD DJANGO_SUPERUSER_EMAIL