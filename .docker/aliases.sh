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
alias regu="docker exec -it ip2tor-shop-django-http /usr/share/restart-gunicorn.sh"

alias onion='docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname'
# Onion address of the sample hidden service
alias onion2='docker exec -it ip2tor-shop-sample-hidden-service cat /var/lib/tor/sample_hidden_service/hostname'

alias d='sudo docker-compose down'
alias b='sudo docker-compose build'
alias u='sudo docker-compose up -d && sudo docker-compose logs -f'
alias dbu='sudo docker-compose down && sudo docker-compose build && sudo docker-compose up -d && sudo docker-compose logs -f'

alias off='sudo shutdown now'
alias doff='sudo docker-compose down && sudo shutdown now'
alias restart='sudo reboot now'

alias dlogs='docker-compose logs -f --tail="20"'

# Aliases for the Host(s)
alias hello='docker exec -it ip2tor-host ip2tor_host.sh hello'
alias activate='docker exec -it ip2tor-host ip2tor_host.sh activate'
alias checkin='docker exec -it ip2tor-host ip2tor_host.sh checkin 0 "Manual HELLO message"'
alias suspend='docker exec -it ip2tor-host ip2tor_host.sh suspend'

alias hd='sudo docker-compose down'
alias hb='sudo docker-compose build'
alias hu='sudo docker-compose up -d && sudo docker-compose logs -f'
alias hdbu='sudo docker-compose down && sudo docker-compose build && sudo docker-compose up -d && sudo docker-compose logs -f'

alias status='docker exec -it ip2tor-host supervisorctl status'
alias sync='docker exec -it ip2tor-host ip2tor_host.sh sync'
alias log='docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/supervisord.log'
alias logip2tor='docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/ip2tor_host-stdout.log'
alias elogip2tor='docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/ip2tor_host-stderr.log'
alias logtor='docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/tor-stdout.log'
alias elogtor='docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/tor-stderr.log'

# Get the stdout logs of a bridge, passing the port number as an argument
# E.g. "logbridge 21212" will return the contents of the file "ip2tor_bridge_21212-stdout.log"
# You can replace $1 with $@ if you  want multiple args.
alias logbridge='f(){ docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/ip2tor_bridge_$1-stdout.log; unset -f f; }; f'
# Get the stdout error logs of a bridge, passing the port number as an argument
# E.g. "elogbridge 21212" will return the contents of the file "ip2tor_bridge_21212-stderr.log"
alias elogbridge='f(){ docker exec -it ip2tor-host cat /home/ip2tor/logs/supervisor/ip2tor_bridge_$1-stderr.log; unset -f f; }; f'