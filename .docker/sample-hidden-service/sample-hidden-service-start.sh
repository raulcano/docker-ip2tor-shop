#!/bin/sh
chown -R debian-tor:debian-tor /var/lib/tor/sample_hidden_service/
chmod -R 700 /var/lib/tor/sample_hidden_service
echo 'Starting Tor for the sample HTTP service...'
exec runuser -u debian-tor "$@"