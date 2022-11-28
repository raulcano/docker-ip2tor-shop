# IP2TOR Shop - Docker files
This repository includes the structure to deploy the ip2tor shop using Docker compose.

The content deployed is based on this repository https://github.com/frennkie/django-ip2tor . which I have forked and introduced some minor changes here: https://github.com/raulcano/ip2tor.

# TL;DR

Assuming you have Docker installed in your system, go to your directory of choice and run the following:


```
git clone https://github.com/raulcano/docker-ip2tor-shop.git
cd docker-ip2tor-shop
```
- _Adjust the environment variables in .env (see below)_  
- _Adjust the CSRF_TRUSTED_ORIGINS variable in .docker/patch/settings.py (see below)_

```
docker compose build
docker compose up
```

To take advantage of Docker's isolation principles, the following containers are created:
- nginx
- django-http  
    - _Here is where the main app stuff happens, plus a http server is started)_
- django-daphne
- redis
- postgres
- celery-beat
- celery-worker
- tor
    - _This container is not mandatory, but useful to generate a hidden service to access your shop)_

# Getting started

By default, the shop will accept connections via Tor on the port 80.
Ensure no other app is using that one.  
E.g.:  
```sudo service apache2 stop```

Open the .env file in the root folder and ensure you introduced the correct values for the database


```
# This variables are setting up the postgres container
POSTGRES_USER=<your_user>
POSTGRES_PASSWORD=<your_password>
POSTGRES_DB=ip2tor_shop #you can leave this or add any of your choice


# This variables are for the django app
# If using the postgres database, then we need to fill the URL with the same values as above
DATABASE_URL="postgres://<your_user>:<your_password>@postgres:5432/ip2tor_shop"
EMAIL_URL="submission://sender@example.com:password@smtp.exmaple.com:587/"

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

# Docker bind mounts
The root folder of the project (where the ```docker-compose.yml``` lives) is mounted in some containers as ```/home/ip2tor```. You'll identify that by the following line in the ```docker-compose.yml``` file.
```
volumes:
    - .:/home/ip2tor
```

Additionally, once the ```tor``` service runs successfully for the first time, the folder ```.tor``` will be created in the root directory. This ```.tor``` folder contains the relevant data for the hidden service and onion address.
```
volumes:
    - .tor/ip2tor-shop_hidden_service:/var/lib/tor/ip2tor-shop_hidden_service/
```
# .docker/start.sh
This script is used to automatize all tasks concerning the startup of these containers:
- django-http
- django-daphne
- celery-beat
- celery-worker

Among other things, this script sets up the Python environment, run migrations for the database and collects the static data from django.

After all the preparation instructions are run, the script executes the service depending on which container called it (django-http, django-daphne, celery-beat or celery-worker).

# .docker/start-tor.sh
This script ensures two things in order to correctly run ```tor```.
- That the ```tor``` service is run with the correct user.
- That the mounted directory has the correct permissions (i.e. 750). If left with the default permissions, tor would complain that the folder is "too permissive".

# ip2tor/django_ip2tor/settings.py

This variable needs to be updated accordingly. E.g.:  
```CSRF_TRUSTED_ORIGINS=['http://localhost:8000']```

For development, you don't need to do anything if you log into your Django admin pages from ```localhost:8000```, but once you deploy to production or use a different port, then you'll have to add the proper values.

I haven't tested it yet, but I suppose you need to add there also the ONION address if you are using one for your shop.

# Shop - admin pages
Once the containers are up, visit your site admin pages. E.g.:  
```localhost:8000/admin```

There, you log in with the ```DJANGO_SUPERUSER_NAME``` and ```DJANGO_SUPERUSER_PASSWORD``` you configured in the ```.env``` file.  

Once in:
- go to Sites, change the initial domain name and display name
- go to User, create a user with the name 'operator' and add it to "operators" group
- go to Hosts and create your first host

## Host ID (IP2TOR_HOST_ID)

Every time you add a host in the Hosts table in the Shop admin interface, its host ID will be generated automatically.  

- Go to the host admin page and add a host with the relevant data: ```http://localhost:8000/admin/shop/host/add/```
- List all hosts in the admin page and get the ID from the ID column on the table, for the host you just added: ```http://localhost:8000/admin/shop/host/```

The format is something like this: ```58b61c0b-0a00-0b00-0c00-0d0000000000```.  

This value is necessary for the configuration of the host, and __needs to be pasted in the host's .env file__:
```IP2TOR_HOST_ID=whatever_value_you_get_as_host_id_after_adding_a_host```  


## Host Token (IP2TOR_HOST_TOKEN)
After you have added a host successfully to the Hosts table

# Other tips & tricks

## How to get the onion address to your shop
Once the docker containers are up, you can type the following in the terminal (root folder of the shop, outside the containers):
```
docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname
```
You can also create an alias in your local terminal, to make that call easier:
```
alias onion='docker exec -it ip2tor-shop-tor cat var/lib/tor/ip2tor-shop_hidden_service/hostname'
```
After running that last command, you'll get your onion address simply by typing ```onion```.

## How to reset the onion address
Delete the .tor folder in the root folder of our shop.  
Next time the container is built, it will create the corresponding folder and add new files with a new address.

__WARNING__: By doing this, you'll lose the address permanently, so be sure to make a backup of the ```tor``` folder if you want to reuse it at a later time.

## Updating settings without having to modify the repo (DEPRECATED)
At the moment, just go to the ip2tor/django_ip2tor/settings.py file and update as necessary.

Originally I designed this structure to patch the settings file with an editable copy at the .docker/patch folder.
There, you'll find the settings.py file, which will overwrite the one downloaded the repo, so you can update some stuff there if necessary without modifying the original settings file in the django folder.

You could still use this way if you prefer, but you'll have to add a line in the start.sh script:
```cp /home/ip2tor/.docker/patch/settings.py /home/ip2tor/ip2tor/django_ip2tor/settings.py```
