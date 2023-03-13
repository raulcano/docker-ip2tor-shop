#!/bin/bash

# You can have a cronjob calling this script from the machine in which the shop is hosted 
# For this, you need to:
#
# Make the script executable
# chmod +x ~/docker-ip2tor-shop/scripts/renew-cert.sh
# 
# Edit the crontab:
# crontab -e
# 
# And add this line (e.g. this would run the script every monday at 3am)
# 0 3 * * mon ~/docker-ip2tor-shop/scripts/renew-cert.sh

source /home/ip2tor/docker-ip2tor-shop/.env
sudo certbot renew

cp /etc/letsencrypt/live/${SHOP_SITE_DOMAIN}/privkey.pem /home/ip2tor/docker-ip2tor-shop/ssl/${SHOP_SITE_DOMAIN}/privkey.pem
cp /etc/letsencrypt/live/${SHOP_SITE_DOMAIN}/fullchain.pem /home/ip2tor/docker-ip2tor-shop/ssl/${SHOP_SITE_DOMAIN}/fullchain.pem