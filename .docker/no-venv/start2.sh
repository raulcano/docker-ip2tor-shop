#!/usr/bin/env bash

role=${CONTAINER_ROLE:-django}

sudo su - ip2tor

if [ "$role" = "django" ]; then

  mkdir /home/ip2tor/ip2tor
  git clone https://github.com/raulcano/ip2tor ip2tor
  cd /home/ip2tor/ip2tor

  echo "App role (Django) ..."
  
 
  source /home/ip2tor/.env

  if [ ! -f "/home/ip2tor/ip2tor/.env" ]; then
    touch .env
    echo -e 'DEBUG=false' | tee --append .env
    
    # add the database URL, email URL and admin data from the root .env file
    echo -e 'DATABASE_URL="'$DATABASE_URL'"' | tee --append .env
    echo -e 'EMAIL_URL="'$EMAIL_URL'"' | tee --append .env
    echo -e 'ADMIN_NAME="'$ADMIN_NAME'"' | tee --append .env
    echo -e 'ADMIN_EMAIL="'$ADMIN_EMAIL'"' | tee --append .env
    
    # add the secret key
    python3 /home/ip2tor/.docker/get-secret-key.py | tee --append .env
  fi

  mkdir /home/ip2tor/media
  mkdir /home/ip2tor/static

  # patch the files with the changes I have introduced in the code downloaded from Github
  cp /home/ip2tor/.docker/patch/settings.py /home/ip2tor/ip2tor/django_ip2tor/settings.py
  cp /home/ip2tor/.docker/patch/lninvoice-signals.py /home/ip2tor/ip2tor/charged/lninvoice/signals.py
  cp /home/ip2tor/.docker/patch/lnnode-signals.py /home/ip2tor/ip2tor/charged/lnnode/signals.py
  cp /home/ip2tor/.docker/patch/views.py /home/ip2tor/ip2tor/shop/api/v1/views.py
  # We enable a custom command in shop/management/commands because the default superuser creation could not be automatized
  cp /home/ip2tor/.docker/createsuperuser_programatically.py /home/ip2tor/ip2tor/shop/management/commands/createsuperuser_programatically.py

  # Run django setup jobs
  python3 manage.py collectstatic <<<yes # confirm overwrite if the folder already contains files
  python3 manage.py makemigrations  # should normally not create new migrations!
  python3 manage.py migrate
  python3 manage.py createsuperuser_programatically --user=$DJANGO_SUPERUSER_NAME --password=$DJANGO_SUPERUSER_PASSWORD --email=$DJANGO_SUPERUSER_EMAIL

  # Limit access rights to base and media directory
  # chmod 700 /home/ip2tor/ip2tor  # !!! uncomment after debugging
  
  # Leaving r-x in Other for both folders, since we need to copy this data in the nginx container
  chmod -R 755 /home/ip2tor/media 
  chmod -R 755 /home/ip2tor/static


  cd /home/ip2tor/ip2tor
  echo "Starting Django in port 8001... "
  /home/ip2tor/venv/bin/daphne -b 0.0.0.0 -p 8001 --proxy-headers django_ip2tor.asgi:application
  # python manage.py runserver 0.0.0.0:8001


elif [ "$role" = "celery-beat" ] || [ "$role" = "celery-worker" ]; then
cd /home/ip2tor/ip2tor
echo "Celery role ..."
cat <<EOF | sudo tee "/etc/tmpfiles.d/ip2tor.conf" >/dev/null
d /run/ip2tor 0755 ip2tor ip2tor -
d /var/log/ip2tor 0755 ip2tor ip2tor -
EOF
sudo systemd-tmpfiles --create --remove
sudo install -m 0644 -o root -g root -t /etc/ /home/ip2tor/ip2tor/contrib/ip2tor-celery.conf
source /etc/ip2tor-celery.conf

  if [ "$role" = "celery-beat" ]; then
    echo "Starting Celery beat ..."
    ${CELERY_BIN} -A ${CELERY_APP} beat  \
    --pidfile=${CELERYBEAT_PID_FILE} \
    -s ${CELERYBEAT_SCHEDULE_FILE} \
    --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler

  elif [ "$role" = "celery-worker" ]; then
    echo "Starting Celery worker ..."
    ${CELERY_BIN} multi start ${CELERYD_NODES} \
    -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
    --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}
  fi

else
    echo "Could not match the container role \"$role\""
    exit 1
fi

# unset POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB DATABASE_URL EMAIL_URL ADMIN_NAME ADMIN_EMAIL DJANGO_SUPERUSER_NAME DJANGO_SUPERUSER_PASSWORD DJANGO_SUPERUSER_EMAIL