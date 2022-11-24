# IP2TOR Shop - Docker files
This repository includes the structure to deploy the ip2tor shop using Docker compose.

The content deployed is based on this repository https://github.com/frennkie/django-ip2tor .  

# TL;DR

Assuming you have Docker installed in your system, go to your directory of choice and run the following:


```
git clone https://github.com/raulcano/docker-ip2tor-shop.git
cd docker-ip2tor-shop
```
_Adjust the .env variables (see below)_  

```
docker compose build
docker compose up
```

To take advantage of Docker's isolation principles, the following containers are created:
- nginx
- django (here is where the main app stuff happens)
- redis
- postgres
- celery-beat
- celery-worker
- tor (this one is not mandatory, but useful to generate a hidden service to access your shop)

# Getting started

By default, the shop will accept connections via Tor on the port 80.
Ensure no other app is using that one.
E.g.:  
```sudo service apache2 stop```

Open the .env file in the root folder and ensure you introduced the correct values for the database


```
# This variables are setting up the postgres container
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=ip2tor_shop #you can leave this or add any of your choice


# This variables are for the django app
# If using the postgres database, then we need to fill the URL with the same values as above
DATABASE_URL="postgres://user:password@postgres:5432/ip2tor_shop"
EMAIL_URL="submission://sender@example.com:password@smtp.exmaple.com:587/"
ADMIN_NAME="shop_admin"
ADMIN_EMAIL="shop_admin@email.com"

DJANGO_SUPERUSER_NAME="shop_admin"
DJANGO_SUPERUSER_PASSWORD="..."
DJANGO_SUPERUSER_EMAIL="shop_admin@email.com"
```

Save changes in the .env file and build the containers

```
docker compose build
docker compose up
```

The first time composer runs, it will download from Git the ip2tor app and put it in the root directory. After that, it won’t download again the repo.

If you want to start fresh, delete that directory, next time we run “docker compose up”, it will be downloaded.


## Updating settings without having to modify the repo
Have a look at the .docker/patch folder.
There, you'll find the settings.py file, which will overwrite the one downloaded from the repo, so you can update some stuff there if necessary.


## How to get the onion address to your shop
Once the docker containers are up
```
docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname
```

## How to reset the onion address
Delete the .tor folder in the root folder of our shop.  
Next time the container is built, it will create the corresponding folder and add new files with a new address

