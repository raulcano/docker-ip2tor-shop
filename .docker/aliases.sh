#!/bin/bash

# I tried creating a service to load on startup , but that didn't work for aliases (for other functions this might be useful)
# see here: https://linuxconfig.org/how-to-run-script-on-startup-on-ubuntu-20-04-focal-fossa-server-desktop

# It turns out that aliases won't be loaded in the system if they run via a script like this:
# https://stackoverflow.com/questions/24054154/how-do-create-an-alias-in-shell-scripts

# In the end, in order to load these aliases in your system, I added them to ~/.bashrc by loading this file, like this:

# if [ -f /path/to/aliases.sh ]; then
# . /path/to/aliases.sh
# fi

# Instructions found here: https://stackoverflow.com/questions/3952033/how-can-i-automatically-load-alias-on-startup#3952039

alias test='docker exec ip2tor-shop-django-http pytest /home/ip2tor/ip2tor/'
alias stest='sudo docker exec ip2tor-shop-django-http pytest /home/ip2tor/ip2tor/'

alias nginx='docker-compose up -d --no-deps --build nginx'
alias snginx='sudo docker-compose up -d --no-deps --build nginx'

alias dhttp='docker-compose up -d --no-deps --build django-http'
alias sdhttp='sudo docker-compose up -d --no-deps --build django-http'


#restarting containers and services
alias regu="sudo docker exec -it ip2tor-shop-django-http /usr/share/restart-gunicorn.sh"

alias onion='sudo docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname'
# Onion address of the sample hidden service
alias onion2='sudo docker exec -it ip2tor-shop-sample-hidden-service cat /var/lib/tor/sample_hidden_service/hostname'

alias d='sudo docker-compose down'
alias b='sudo docker-compose build'
alias u='sudo docker-compose up -d && sudo docker-compose logs -f'
alias dbu='sudo docker-compose down && sudo docker-compose build && sudo docker-compose up -d && sudo docker-compose logs -f'

alias off='sudo shutdown now'
alias doff='sudo docker-compose down && sudo shutdown now'
alias restart='sudo reboot now'

alias dlogs='sudo docker-compose logs -f --tail="20"'
alias hostids='sudo docker exec -it ip2tor-shop-django-http python3 /home/ip2tor/ip2tor/manage.py get_host_ids_and_tokens'

alias fstatus='sudo ufw status'
alias psql='sudo docker exec -it ip2tor-shop-postgres psql --username=shopolite --dbname=ip2tor_shop'
alias sizes='sudo find . -type f -exec du -Sh {} + | sort -rh | head -n 20'