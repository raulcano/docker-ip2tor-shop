# IP2TOR Shop - Docker files
This repository includes the structure to deploy the ip2tor shop using Docker compose.

The content deployed is based on this repository https://github.com/frennkie/django-ip2tor. 

# TL;DR

Assuming you have Docker installed in your system, go to your directory of choice and run the following:


```
git clone https://github.com/raulcano/docker-ip2tor-shop.git
cd docker-ip2tor-shop
```
- _Adjust the environment variables in .env (see below)_  
- _Adjust the CSRF_TRUSTED_ORIGINS variable in ip2tor/django_ip2tor/settings.py (see below)_

```
docker compose build
docker compose up
```

To take advantage of Docker's isolation principles, the following containers are created:
- nginx
    - _A reverse proxy, directing requests to the main services to the right URLs and ports_ 
- django-http  
    - _Here is where the main app stuff happens, plus a http server is started_
- django-daphne
    - _A server for the asgi elements of the app_
- redis
    - _A message broker and cache service_
- postgres
    - _The database_
- celery-beat
    - _A task scheduler_
- celery-worker
    - _A worker for background tasks_
- celery-flower
    - _A dashboard for monitoring tasks and workers_
- tor
    - _This container is not mandatory, but useful to generate a hidden service to access your shop)_

# Getting started

By default, the shop will accept connections via Tor on the port 80.
Ensure no other app is using that one.  
E.g.:  
```sudo service apache2 stop```

Open the .env file in the ip2tor folder and ensure you introduced the correct values for the database


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
After you have added a host successfully to the Hosts table, visit the admin tokens page: ```http://localhost:8000/admin/authtoken/tokenproxy/```

In the column "User", YOU will find a row with the same Host ID of the host we just generated. There, the token is the value under the "Key" column. 

The format is something like this: ```4oik58db29fba90761da646e06asd82d00ef0000```

This value is necessary for the configuration of the host, and __needs to be pasted in the host's .env file__:
```IP2TOR_HOST_TOKEN=whatever_token_you_get_for_your_host_id```  

# Firewall
_To Be Confirmed_  
These firewall commands should be run from the 
```
sudo firewall-cmd --add-service http --permanent  
sudo firewall-cmd --add-service https --permanent
sudo firewall-cmd --reload
```

# Flower
One of the containers include the dashboard Flower (as in 'flow-er'). This app offers a visualization of the celery tasks and workers and is useful for its monitoring.

Once the docker compose is up and running, you need to access ```localhost:5555``` to open Flower.

![Flower screenshot](images/flower.png)

# Other tips & tricks

## Always leave a new empty line at the end of the .env file
The reason is that the secret key is generated programatically and appended at the end of the file. If there is no new line, it will be pasted just in the same line of the last env variable, which will mess things up.

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

## What is the workflow to create a (Raspiblitz) subscription to a Host bridge?
Check the discussion in this thread. While things might have changed since then, the steps can be of help to understand the API functions:
https://github.com/rootzoll/raspiblitz/issues/1194#issuecomment-632075264

To place the order and issue the first payment:

- Retrieve Host list: GET https://shop.ip2t.org/api/v1/public/hosts/
- Place Purchase Order: POST https://shop.ip2t.org/api/v1/public/order/ (store the resulting ID/URL)
- wait a few ms
- Retrieve Purchase Order: GET https://shop.ip2t.org/api/v1/public/pos/22a942b3-89de-48e4-841c-f15d4d21e69f/ (store both item_details[0] (e.g. in order to extend life time of bridge later) and ln_invoices[0] <- if empty repeat until a value shows up)
- wait a few seconds (this is a looping script running every 5-30 seconds)
- Retrieve LN Invoice : GET https://shop.ip2t.org/api/v1/public/po_invoices/1b7fe1ce-0ba6-4c74-81de-bbd304261fb4/
- Pay to payment_request
- Status of LN Invoice should change to 2.
- Check implementation status (PO: item_details[0].object_id (ToDo: flatten this ..!): GET https://shop.ip2t.org/api/v1/public/tor_bridges/0f25a0b7-e261-44eb-a01b-0b2b25981c68/ status should change to "A".


To extend an existing subscription:

- empty POST to https://shop.ip2t.org/api/v1/public/tor_bridges/0f25a0b7-e261-44eb-a01b-0b2b25981c68/extend/ (store po)
- Retrieve Purchase Order: GET https://shop.ip2t.org/api/v1/public/pos/a22843b6-a2dd-4742-a97e-15fcb395847a/
- wait a few seconds (this is a looping script running every 5-30 seconds)
- Retrieve LN Invoice : GET https://shop.ip2t.org/api/v1/public/pos/a22843b6-a2dd-4742-a97e-15fcb395847a/
- Pay to payment_request
- status of LN Invoice should change to 2.

## Update nginx configuration and restart nginx container

This may come in handy while developing and trying different nginx configurations. 

Assuming the nginx container is running with a particular configuration, we can:
- Modify the file ```shop.localhost.conf``` in the ```.docker``` folder with a new configuration to test.
- Rebuild the container
- Restart the container

This is the way to achieve that with a simple command (after the config file has been updated, of course):

```
docker compose up -d --no-deps --build nginx
```
Also, we can create an alias for ease of use:
```
alias nconf='docker compose up -d --no-deps --build nginx'
```
After wich, just run ```nconf``` to rebuild your docker nginx container with the new configuration.


## Testing
For testing, we are using the pytest framework.
In order to run the tests across all apps, one needs to run the ```pytest``` command in a container where django is built.

The simplest way to run the tests is to create an alias to send the pytest command to the corresponding container. 
In your host machine, run this:  
```alias test='docker exec ip2tor-shop-django-http pytest /home/ip2tor/ip2tor/'```

After that, run the tests with:  
```test```

## Celery inside a docker container
Docker containers need a foreground task to be running, or the container will exit. Since Celery workers are in the background, the container exits. Therefore, we needed to run the Celery container(s) with a task that remains permanently in the foreground, while the worker is in the background. 

See more details in this post:  
https://stackoverflow.com/questions/48646745/celery-multi-inside-docker-container

## When running docker, I get 'Error while fetching server API version'

_This section is extracted from the comments in this StackOverflow post:
https://stackoverflow.com/questions/64952238/docker-errors-dockerexception-error-while-fetching-server-api-version_


```docker.errors.DockerException: Error while fetching server API version```

By default, the docker command can only be run the root user or by a user in the docker group,
which is automatically created during Docker’s installation process. If you want to avoid typing sudo whenever you run the docker command, add your username to the docker group:

```sudo usermod -aG docker ${USER}```

To apply the new group membership, log out of the server and back in, or type the following:
```su - ${USER}```

If nothing of the above works, try setting the permissions for this file like this:
```sudo chmod 666 /var/run/docker.sock```

## .docker/init-for-host.sh

This is a file for convenience, where you can add some commands and load them on your host machine at startup.

This is not necessary for the system to work, but may be of help if you repeat certain commands, and I have written a few aliases that I ended up using quite frequently.

There are several ways to make this script run on startup, so you just pick your favorite. 
Find some instructions here:

https://raspberrytips.com/run-script-at-startup-on-linux/

## Certificates for the Lightning Node(s)
We can generate a self-signed certificate for the node for our tests with this command.  
Change the ip ```192.168.0.160``` with the IP from your node.

```
openssl req -x509 -out self-signed.crt -keyout self-signed.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=192.168.0.160' -extensions EXT -config <( \
   printf "[dn]\nCN=192.168.0.160\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:192.168.0.160\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```


## Updating settings without having to modify the repo (DEPRECATED)
At the moment, just go to the ip2tor/django_ip2tor/settings.py file and update as necessary.

Originally I designed this structure to patch the settings file with an editable copy at the .docker/patch folder.
There, you'll find the settings.py file, which will overwrite the one downloaded the repo, so you can update some stuff there if necessary without modifying the original settings file in the django folder.

You could still use this way if you prefer, but you'll have to add a line in the start.sh script:
```cp /home/ip2tor/.docker/patch/settings.py /home/ip2tor/ip2tor/django_ip2tor/settings.py```


# Shop APPS and API endpoints
## APP: ```shop```



```/shop/demo```

views.DemoView.as_view()

name='demo'

 

```/shop/hosts/```

views.HostListView.as_view()

name='host-list'

This view lists all ACTIVE hosts stored in the shop (in the model Host)
  
  
```/shop/hosts/<uuid:pk>/```

views.PurchaseTorBridgeOnHostView.as_view()

name='host-purchase'

Logic to present a purchase form.

If the data is valid:

- A Purchase Order order is created in the ShopPurchaseOrder model.

- The user is redirected to the detail view of the Purchase Order in the app 'lnpurchase' (the link is named 'lnpurchase:po-detail'

    /charged/lnpurchase/po/<uuid:pk>/

 

 

## APP: ```charged/lnpurchase```


```/charged/lnpurchase/po/<uuid:pk>/```

views.PurchaseOrderDetailView.as_view()
name='po-detail'
Shows the detail view of a Purchase Order