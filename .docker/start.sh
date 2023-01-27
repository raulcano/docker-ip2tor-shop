#!/usr/bin/env bash

#Change to service user and install + update virtual python environment
sudo su - ip2tor
cd /home/ip2tor/ip2tor
role=${CONTAINER_ROLE:-django-http}

# This is where the global python packages are installed
# python3 -m site


# We copy the .env variable from the root to the django project. Both the ip2tor app and the docker compose need it in their directory
cp /home/ip2tor/.env /home/ip2tor/ip2tor/.env

if [ "$role" = "django-http" ]; then
  echo "App role (Django HTTP server) ..."

  source /home/ip2tor/ip2tor/.env
  
  if [ -z "$SECRET_KEY" ]; then
    echo 'Generating new secret key...'
    python3 /home/ip2tor/.docker/get-secret-key.py | tee --append .env
  else
    echo 'Secret key was defined already. No new secret key was generated.'
  fi

  mkdir /home/ip2tor/media
  mkdir /home/ip2tor/static

  # Run django setup jobs
  python3 manage.py collectstatic <<<yes # confirm overwrite if the folder already contains files
  python3 manage.py makemigrations  # should normally not create new migrations!
  python3 manage.py migrate
  python3 manage.py createsuperuser_programatically --user=$DJANGO_SUPERUSER_NAME --password=$DJANGO_SUPERUSER_PASSWORD --email=$DJANGO_SUPERUSER_EMAIL
  python3 manage.py create_operator --user=$DJANGO_OPERATOR_NAME --password=$DJANGO_OPERATOR_PASSWORD --email=$DJANGO_OPERATOR_EMAIL
  python3 manage.py create_site --name="$SHOP_SITE_NAME" --domain=$SHOP_SITE_DOMAIN
  if [ "True" = $SHOP_HOST1_REGISTER ]; then
    python3 manage.py create_host --owner=$DJANGO_OPERATOR_NAME --sitedomain="$SHOP_SITE_DOMAIN" --name="$SHOP_HOST1_NAME" --description="$SHOP_HOST1_DESCRIPTION" --ip=$SHOP_HOST1_IP --portranges=$SHOP_HOST1_PORT_RANGES --rangetype=$SHOP_HOST1_PORT_RANGE_TYPE --isenabled=$SHOP_HOST1_IS_ENABLED --isalive=$SHOP_HOST1_IS_ALIVE --istesthost=$SHOP_HOST1_IS_TESTHOST --istestnet=$SHOP_HOST1_IS_TESTNET --offerstorbridges=$SHOP_HOST1_OFFERS_TOR_BRIDGES --torbridgeduration=$SHOP_HOST1_TOR_BRIDGE_DURATION --torbridgepriceinitial=$SHOP_HOST1_TOR_BRIDGE_PRICE_INITIAL --torbridgepriceextension=$SHOP_HOST1_TOR_BRIDGE_PRICE_EXTENSION --offersrsshtunnels=$SHOP_HOST1_OFFERS_RSSH_TUNNELS --rsshtunnelprice=$SHOP_HOST1_RSSH_TUNNEL_PRICE --tos="$SHOP_HOST1_TERMS_OF_SERVICE" --tosurl="$SHOP_HOST1_TERMS_OF_SERVICE_URL" --cistatus=$SHOP_HOST1_CI_STATUS --cidate="$SHOP_HOST1_CI_DATE" --cimessage="$SHOP_HOST1_CI_MESSAGE"
  fi
  if [ "True" = $SHOP_HOST2_REGISTER ]; then
    python3 manage.py create_host --owner=$DJANGO_OPERATOR_NAME --sitedomain="$SHOP_SITE_DOMAIN" --name="$SHOP_HOST2_NAME" --description="$SHOP_HOST2_DESCRIPTION" --ip=$SHOP_HOST2_IP --portranges=$SHOP_HOST2_PORT_RANGES --rangetype=$SHOP_HOST2_PORT_RANGE_TYPE --isenabled=$SHOP_HOST2_IS_ENABLED --isalive=$SHOP_HOST2_IS_ALIVE --istesthost=$SHOP_HOST2_IS_TESTHOST --istestnet=$SHOP_HOST2_IS_TESTNET --offerstorbridges=$SHOP_HOST2_OFFERS_TOR_BRIDGES --torbridgeduration=$SHOP_HOST2_TOR_BRIDGE_DURATION --torbridgepriceinitial=$SHOP_HOST2_TOR_BRIDGE_PRICE_INITIAL --torbridgepriceextension=$SHOP_HOST2_TOR_BRIDGE_PRICE_EXTENSION --offersrsshtunnels=$SHOP_HOST2_OFFERS_RSSH_TUNNELS --rsshtunnelprice=$SHOP_HOST2_RSSH_TUNNEL_PRICE --tos="$SHOP_HOST2_TERMS_OF_SERVICE" --tosurl="$SHOP_HOST2_TERMS_OF_SERVICE_URL" --cistatus=$SHOP_HOST2_CI_STATUS --cidate="$SHOP_HOST2_CI_DATE" --cimessage="$SHOP_HOST2_CI_MESSAGE"
  fi
  if [ "True" = $SHOP_HOST3_REGISTER ]; then
    python3 manage.py create_host --owner=$DJANGO_OPERATOR_NAME --sitedomain="$SHOP_SITE_DOMAIN" --name="$SHOP_HOST3_NAME" --description="$SHOP_HOST3_DESCRIPTION" --ip=$SHOP_HOST3_IP --portranges=$SHOP_HOST3_PORT_RANGES --rangetype=$SHOP_HOST3_PORT_RANGE_TYPE --isenabled=$SHOP_HOST3_IS_ENABLED --isalive=$SHOP_HOST3_IS_ALIVE --istesthost=$SHOP_HOST3_IS_TESTHOST --istestnet=$SHOP_HOST3_IS_TESTNET --offerstorbridges=$SHOP_HOST3_OFFERS_TOR_BRIDGES --torbridgeduration=$SHOP_HOST3_TOR_BRIDGE_DURATION --torbridgepriceinitial=$SHOP_HOST3_TOR_BRIDGE_PRICE_INITIAL --torbridgepriceextension=$SHOP_HOST3_TOR_BRIDGE_PRICE_EXTENSION --offersrsshtunnels=$SHOP_HOST3_OFFERS_RSSH_TUNNELS --rsshtunnelprice=$SHOP_HOST3_RSSH_TUNNEL_PRICE --tos="$SHOP_HOST3_TERMS_OF_SERVICE" --tosurl="$SHOP_HOST3_TERMS_OF_SERVICE_URL" --cistatus=$SHOP_HOST3_CI_STATUS --cidate="$SHOP_HOST3_CI_DATE" --cimessage="$SHOP_HOST3_CI_MESSAGE"
  fi
  if [ "True" = $SHOP_HOST4_REGISTER ]; then
    python3 manage.py create_host --owner=$DJANGO_OPERATOR_NAME --sitedomain="$SHOP_SITE_DOMAIN" --name="$SHOP_HOST4_NAME" --description="$SHOP_HOST4_DESCRIPTION" --ip=$SHOP_HOST4_IP --portranges=$SHOP_HOST4_PORT_RANGES --rangetype=$SHOP_HOST4_PORT_RANGE_TYPE --isenabled=$SHOP_HOST4_IS_ENABLED --isalive=$SHOP_HOST4_IS_ALIVE --istesthost=$SHOP_HOST4_IS_TESTHOST --istestnet=$SHOP_HOST4_IS_TESTNET --offerstorbridges=$SHOP_HOST4_OFFERS_TOR_BRIDGES --torbridgeduration=$SHOP_HOST4_TOR_BRIDGE_DURATION --torbridgepriceinitial=$SHOP_HOST4_TOR_BRIDGE_PRICE_INITIAL --torbridgepriceextension=$SHOP_HOST4_TOR_BRIDGE_PRICE_EXTENSION --offersrsshtunnels=$SHOP_HOST4_OFFERS_RSSH_TUNNELS --rsshtunnelprice=$SHOP_HOST4_RSSH_TUNNEL_PRICE --tos="$SHOP_HOST4_TERMS_OF_SERVICE" --tosurl="$SHOP_HOST4_TERMS_OF_SERVICE_URL" --cistatus=$SHOP_HOST4_CI_STATUS --cidate="$SHOP_HOST4_CI_DATE" --cimessage="$SHOP_HOST4_CI_MESSAGE"
  fi
  if [ "True" = $SHOP_HOST5_REGISTER ]; then
    python3 manage.py create_host --owner=$DJANGO_OPERATOR_NAME --sitedomain="$SHOP_SITE_DOMAIN" --name="$SHOP_HOST5_NAME" --description="$SHOP_HOST5_DESCRIPTION" --ip=$SHOP_HOST5_IP --portranges=$SHOP_HOST5_PORT_RANGES --rangetype=$SHOP_HOST5_PORT_RANGE_TYPE --isenabled=$SHOP_HOST5_IS_ENABLED --isalive=$SHOP_HOST5_IS_ALIVE --istesthost=$SHOP_HOST5_IS_TESTHOST --istestnet=$SHOP_HOST5_IS_TESTNET --offerstorbridges=$SHOP_HOST5_OFFERS_TOR_BRIDGES --torbridgeduration=$SHOP_HOST5_TOR_BRIDGE_DURATION --torbridgepriceinitial=$SHOP_HOST5_TOR_BRIDGE_PRICE_INITIAL --torbridgepriceextension=$SHOP_HOST5_TOR_BRIDGE_PRICE_EXTENSION --offersrsshtunnels=$SHOP_HOST5_OFFERS_RSSH_TUNNELS --rsshtunnelprice=$SHOP_HOST5_RSSH_TUNNEL_PRICE --tos="$SHOP_HOST5_TERMS_OF_SERVICE" --tosurl="$SHOP_HOST5_TERMS_OF_SERVICE_URL" --cistatus=$SHOP_HOST5_CI_STATUS --cidate="$SHOP_HOST5_CI_DATE" --cimessage="$SHOP_HOST5_CI_MESSAGE"
  fi
  if [ "True" = $SHOP_HOST6_REGISTER ]; then
    python3 manage.py create_host --owner=$DJANGO_OPERATOR_NAME --sitedomain="$SHOP_SITE_DOMAIN" --name="$SHOP_HOST6_NAME" --description="$SHOP_HOST6_DESCRIPTION" --ip=$SHOP_HOST6_IP --portranges=$SHOP_HOST6_PORT_RANGES --rangetype=$SHOP_HOST6_PORT_RANGE_TYPE --isenabled=$SHOP_HOST6_IS_ENABLED --isalive=$SHOP_HOST6_IS_ALIVE --istesthost=$SHOP_HOST6_IS_TESTHOST --istestnet=$SHOP_HOST6_IS_TESTNET --offerstorbridges=$SHOP_HOST6_OFFERS_TOR_BRIDGES --torbridgeduration=$SHOP_HOST6_TOR_BRIDGE_DURATION --torbridgepriceinitial=$SHOP_HOST6_TOR_BRIDGE_PRICE_INITIAL --torbridgepriceextension=$SHOP_HOST6_TOR_BRIDGE_PRICE_EXTENSION --offersrsshtunnels=$SHOP_HOST6_OFFERS_RSSH_TUNNELS --rsshtunnelprice=$SHOP_HOST6_RSSH_TUNNEL_PRICE --tos="$SHOP_HOST6_TERMS_OF_SERVICE" --tosurl="$SHOP_HOST6_TERMS_OF_SERVICE_URL" --cistatus=$SHOP_HOST6_CI_STATUS --cidate="$SHOP_HOST6_CI_DATE" --cimessage="$SHOP_HOST6_CI_MESSAGE"
  fi

  if [ "True" = $CHARGED_LND1_REGISTER ]; then
    echo "Trying to create $CHARGED_LND1_CLASS on host $CHARGED_LND1_HOST and port $CHARGED_LND1_PORT {tls_verification=$CHARGED_LND1_TLS_VERIFICATION}"
    python3 manage.py create_node --nodeclass=$CHARGED_LND1_CLASS --name=$CHARGED_LND1_NAME --priority=$CHARGED_LND1_PRIORITY --owner=$CHARGED_LND1_OWNER --macaroon_admin=$CHARGED_LND1_MACAROON_ADMIN --macaroon_invoice=$CHARGED_LND1_MACAROON_INVOICE --macaroon_readonly=$CHARGED_LND1_MACAROON_READONLY --tls_certificate="$CHARGED_LND1_TLS_CERTIFICATE" --tls_verification=$CHARGED_LND1_TLS_VERIFICATION --host=$CHARGED_LND1_HOST --port=$CHARGED_LND1_PORT
  fi
  if [ "True" = $CHARGED_LND2_REGISTER ]; then
    echo "Trying to create $CHARGED_LND2_CLASS on host $CHARGED_LND2_HOST and port $CHARGED_LND2_PORT {tls_verification=$CHARGED_LND2_TLS_VERIFICATION}"
    python3 manage.py create_node --nodeclass=$CHARGED_LND2_CLASS --name=$CHARGED_LND2_NAME --priority=$CHARGED_LND2_PRIORITY --owner=$CHARGED_LND2_OWNER --macaroon_admin=$CHARGED_LND2_MACAROON_ADMIN --macaroon_invoice=$CHARGED_LND2_MACAROON_INVOICE --macaroon_readonly=$CHARGED_LND2_MACAROON_READONLY --tls_certificate="$CHARGED_LND2_TLS_CERTIFICATE" --tls_verification=$CHARGED_LND2_TLS_VERIFICATION --host=$CHARGED_LND2_HOST --port=$CHARGED_LND2_PORT
  fi
  if [ "True" = $CHARGED_LND3_REGISTER ]; then
    echo "Trying to create $CHARGED_LND3_CLASS on host $CHARGED_LND3_HOST and port $CHARGED_LND3_PORT {tls_verification=$CHARGED_LND3_TLS_VERIFICATION}"
    python3 manage.py create_node --nodeclass=$CHARGED_LND3_CLASS --name=$CHARGED_LND3_NAME --priority=$CHARGED_LND3_PRIORITY --owner=$CHARGED_LND3_OWNER --macaroon_admin=$CHARGED_LND3_MACAROON_ADMIN --macaroon_invoice=$CHARGED_LND3_MACAROON_INVOICE --macaroon_readonly=$CHARGED_LND3_MACAROON_READONLY --tls_certificate="$CHARGED_LND3_TLS_CERTIFICATE" --tls_verification=$CHARGED_LND3_TLS_VERIFICATION --host=$CHARGED_LND3_HOST --port=$CHARGED_LND3_PORT
  fi
  if [ "True" = $CHARGED_LND4_REGISTER ]; then
    echo "Trying to create $CHARGED_LND4_CLASS on host $CHARGED_LND4_HOST and port $CHARGED_LND4_PORT {tls_verification=$CHARGED_LND4_TLS_VERIFICATION}"
    python3 manage.py create_node --nodeclass=$CHARGED_LND4_CLASS --name=$CHARGED_LND4_NAME --priority=$CHARGED_LND4_PRIORITY --owner=$CHARGED_LND4_OWNER --macaroon_admin=$CHARGED_LND4_MACAROON_ADMIN --macaroon_invoice=$CHARGED_LND4_MACAROON_INVOICE --macaroon_readonly=$CHARGED_LND4_MACAROON_READONLY --tls_certificate="$CHARGED_LND4_TLS_CERTIFICATE" --tls_verification=$CHARGED_LND4_TLS_VERIFICATION --host=$CHARGED_LND4_HOST --port=$CHARGED_LND4_PORT
  fi
  if [ "True" = $CHARGED_LND5_REGISTER ]; then
    echo "Trying to create $CHARGED_LND5_CLASS on host $CHARGED_LND5_HOST and port $CHARGED_LND5_PORT {tls_verification=$CHARGED_LND5_TLS_VERIFICATION}"
    python3 manage.py create_node --nodeclass=$CHARGED_LND5_CLASS --name=$CHARGED_LND5_NAME --priority=$CHARGED_LND5_PRIORITY --owner=$CHARGED_LND5_OWNER --macaroon_admin=$CHARGED_LND5_MACAROON_ADMIN --macaroon_invoice=$CHARGED_LND5_MACAROON_INVOICE --macaroon_readonly=$CHARGED_LND5_MACAROON_READONLY --tls_certificate="$CHARGED_LND5_TLS_CERTIFICATE" --tls_verification=$CHARGED_LND5_TLS_VERIFICATION --host=$CHARGED_LND5_HOST --port=$CHARGED_LND5_PORT
  fi


  # Display the string of Host IDs and Tokens needed for each Host (to be added in the .env file of the machine hosting those hosts)
  python3 manage.py get_host_ids_and_tokens
  
  # Limit access rights to base and media directory
  # chmod 700 /home/ip2tor/ip2tor  # !!! uncomment after debugging
  
  # Leaving r-x in Other for both folders
  chmod -R 755 /home/ip2tor/media 
  chmod -R 755 /home/ip2tor/static

  # This was to test if we can add LND nodes with Tor address
  # echo "Starting Tor in Django HTTP container..."
  # sudo service tor start
  
  echo "Starting Django HTTP server in port "$DJANGO_HTTP_PORT"... "
  # python3 manage.py runserver 0.0.0.0:$DJANGO_HTTP_PORT
  gunicorn --bind=0.0.0.0:$DJANGO_HTTP_PORT django_ip2tor.wsgi
  
elif [ "$role" = "django-daphne" ]; then
  source /home/ip2tor/ip2tor/.env
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
        echo "Signal caught..."
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
  

  elif [ "$role" = "celery-beat" ]; then
    echo "Starting Celery beat ..."
    ${CELERY_BIN} -A ${CELERY_APP} beat  \
    --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
    # -s ${CELERYBEAT_SCHEDULE_FILE} \ # I don't think this is an argument for celery beat - see here https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#generic-initd-celerybeat-options
    # --pidfile=${CELERYBEAT_PID_FILE} \
  fi


else
    echo "Could not match the container role \"$role\""
    exit 1
fi

# unset POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB DATABASE_URL EMAIL_URL ADMIN_NAME ADMIN_EMAIL DJANGO_SUPERUSER_NAME DJANGO_SUPERUSER_PASSWORD DJANGO_SUPERUSER_EMAIL