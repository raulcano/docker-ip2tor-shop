alias test='docker exec ip2tor-shop-django-http pytest /home/ip2tor/ip2tor/'
alias stest='sudo docker exec ip2tor-shop-django-http pytest /home/ip2tor/ip2tor/'

alias nginx='docker-compose up -d --no-deps --build nginx'
alias snginx='sudo docker-compose up -d --no-deps --build nginx'

alias dhttp='docker-compose up -d --no-deps --build django-http'
alias sdhttp='sudo docker-compose up -d --no-deps --build django-http'

alias regu="docker exec -it ip2tor-shop-django-http /usr/share/restart-gunicorn.sh"

alias onion='docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname'