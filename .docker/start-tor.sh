#!/bin/sh

chown -R debian-tor:debian-tor /var/lib/tor/ip2tor-shop_hidden_service/
chmod -R 700 /var/lib/tor/ip2tor-shop_hidden_service
exec runuser -u debian-tor "$@"