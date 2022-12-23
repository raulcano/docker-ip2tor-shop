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

alias regu="docker exec -it ip2tor-shop-django-http /usr/share/restart-gunicorn.sh"

alias onion='docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname'

alias dbu='sudo docker-compose down && sudo docker-compose build && sudo docker-compose up'
