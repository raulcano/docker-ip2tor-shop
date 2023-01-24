# IP2TOR Shop - Docker files
This repository includes the structure to deploy the ip2tor shop using Docker compose.

The content deployed is based on this repository https://github.com/frennkie/django-ip2tor.
__NOTE:__ These instructions correspond to a host machine running Ubuntu 22.04.1 LTS.s

# TL;DR

Assuming you have Docker installed in your system, go to your directory of choice and run the following:


```
git clone https://github.com/raulcano/docker-ip2tor-shop.git
cd docker-ip2tor-shop
```
- _Adjust the environment variables in .env (see below)_  

Create a link of the .env file
```
ln /home/ip2tor/docker-ip2tor-shop/.env /home/ip2tor/docker-ip2tor-shop/ip2tor/.env
```

Run docker

```
docker compose build
docker compose up
```

Once Docker is running, several services will be available in these containers:
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
- sample-http
    - _A simple "Hello World!" http service that responds after calling it. Useful for tests_
- sample-hidden-service
    - _Generates a hidden service for the 'sample-http' container. Useful for tests_


# Getting started

By default, the shop will accept connections via Tor on the port 80.
Ensure no other app is using that one.  
E.g.:  
```sudo service apache2 stop```

Open the .env file in the ip2tor folder and ensure you introduced the correct values for the database and the many other variables that are in the file.

One thing not to forget is this variable, which needs to be updated accordingly. E.g.:  
```CSRF_TRUSTED_ORIGINS=['http://localhost:8000']```

For development, you don't need to do anything if you log into your Django admin pages from ```localhost:8000```, but once you deploy to production or use a different port, then you'll have to add the proper values.

I haven't tested it yet, but I suppose you need to add there also the ONION address if you are using one for your shop.

The ```.env``` contains quite a lot of options of configuration, so things are kept in one place as far as possible. Pay attention to the variables and take your time understanding what you are doing.


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

# Shop class diagram
This is a complex system that has plenty of classes and elements carefully working together. In order to help me understand the role and relationships of all moving parts, I created the following class diagram. It is not exact or perfectly complete, as I have reverse engineered it as needed, but it has the most relevant aspects.

![IP2Tor class diagram](images/ip2tor_shop_class_diagram.png)

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
- celery-flower

Among other things, this script sets up the Python environment, run migrations for the database and collects the static data from django.

After all the preparation instructions are run, the script executes the service depending on which container called it.

# .docker/start-tor.sh
This script ensures two things in order to correctly run ```tor```.
- That the ```tor``` service is run with the correct user.
- That the mounted directory has the correct permissions (i.e. 750). If left with the default permissions, tor would complain that the folder is "too permissive".

# Shop - admin pages
Once the containers are up, visit your site admin pages. E.g.:  
```localhost:8000/admin```

There, you log in with the ```DJANGO_SUPERUSER_NAME``` and ```DJANGO_SUPERUSER_PASSWORD``` you configured in the ```.env``` file.  

Once in:
- go to Sites, check and, if needed, change the initial domain name and display name
- go to User, check and, if needed, create a user with the name 'operator' and add it to "operators" group
- go to Hosts check and, if needed, and create new hosts

The initial creation of Site(s), User(s) and Host(s) is automatized on the first run of the docker container, based on the values of the ```.env``` variable.

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
__IMPORTANT__: These steps need to be run in the main machine where we are running all Shop containers, not in any container in particular.
We'll be using ```ufw``` as our firewall, even though other options are available for you to choose.
These steps are to ensure that, by default, only these ports will be allowed for incoming traffic:
- SSH (22)
- HTTP (80)
- HTTPS (443)
- 9050


First, we install ```ufw``` if not available:
```
sudo apt-get install ufw
```

To check the firewall status:
```
sudo ufw status
```

To check which ports are open, we can use any of these commands:
```
netstat -lntu
# or 
ss -lntu
```

Also, to check if a port is used, run any of these lines (in the example, we check if port 22 is open). If the output is blank, it means the port is not being used.
```
netstat -na | grep :22
# or
ss -na | grep :22
```

By default, we block all incoming traffic and allow all outgoing
```
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

Now we allow the ports of our choosing for incoming traffic
```
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 9050
```

Ensure ```ufw``` is enabled
```
sudo ufw enable
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

Note: find more info in this link about the nginx container and how we are using our configuration in the docker-compose file: https://github.com/docker-library/docs/tree/master/nginx#using-environment-variables-in-nginx-configuration

This may come in handy while developing and trying different nginx configurations. 

Assuming the nginx container is running with a particular configuration, we can:
- Modify the file ```default.conf.template``` in the ```.docker/nginx``` folder with a new configuration to test.
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

## How to tail Docker logs
After starting the docker compose, you will get the logs of each container in your terminal. If you close the terminal and come back later, this is how to get those logs run on your screen.

  

__For tailing ONLY ONE or SELECTED containers__
```
docker-compose logs -f -t <service name 1> <service name 2> ... <service name N>
```
For example:
```
docker-compose logs -f -t tor nginx django-http
```

__For tailing ALL containers__
```
docker-compose logs -f -t
```

That's it.


Find more info about this in this very interesting article:  
https://www.papertrail.com/solution/tips/how-to-live-tail-docker-logs/  
or here  
https://stackoverflow.com/questions/37195222/how-to-view-log-output-using-docker-compose-run



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
Every time the LND node is restarted, LND will generate self-signed certificates valid to establish secure channels via REST or gRPC.

The only thing we need to ensure is that the IP with which we are accessing our node is within the IPs of the self-signed certificate. (i.e. env variable CHARGED_LND_HOST)



In short, connect to the node and edit the file ```lnd.conf```. In the Raspiblitz, it can be found within the directory ```/home/bitcoin/.lnd```

Add as many of these lines as needed. In my case, I added the following, since the shop and the LND node are in the same local network, so I configured CHARGED_LND_HOST with a LAN IP address.
```
...
tlsextraip=192.168.0.60
tlsextraip=127.0.0.1
tlsextradomain=localhost
...
```

More details can be found here: https://docs.zaphq.io/docs-desktop-lnd-configure

After the previous is done, two more steps.
Remove the existing certs:
```
sudo rm ~/.lnd/tls.cert ~/.lnd/tls.key
```

And restart the node
```
sudo reboot now
```

After the LND reboot is successful and the node is working fine, you can access the TLS cert. In the case of the Raspiblitz, just do this:
```
cat /home/bitcoin/.lnd/tls.cert
```

 Copy the result into the variable ```CHARGED_LND_TLS_CERTIFICATE``` within the .env file.
 ```
 # PEM Formatted, add text here. For some reason, if you add it in one line, there is an error, so you need to keep the BEGIN and END lines separate

CHARGED_LND_TLS_CERTIFICATE="-----BEGIN CERTIFICATE-----
...
ALL/CERT/STRINGS/GO/HERE
...
-----END CERTIFICATE-----"
 ```

## If you reset the Lightning Node, you need to add the new cert to the node in the shop
At least with Raspiblitz, if the node is restarted, you need to retrieve the new cert and update the node stored in the shop with it. This command will print it in the screen:

```cat /home/bitcoin/.lnd/tls.cert```

Once displayed, you can replace that directly from the admin menu in the django shop or add it to the .env variables, remove the node from django and restart the container.

## Checking if hosts are alive
There is a task that runs periodically to check the status of the enabled hosts.

For more info, see the task ```host_alive_check``` and the Host method ```check_alive_status```.
In short, for the host to be considered alive, the check-in message in the Host instance must be HELLO and the time must not be more than 5 minutes ago from the current time.
It is important to notice that the alive check on hosts looks in the local database when was the last time they did a checkin: if it was more than 5 minutes ago, the host is considered NOT ALIVE.




## Get Telegraf config

Using httpie (easy CLI http client)

```
http GET http://127.0.0.1:8000/api/v1/tor_bridges/?host=58b61c0b-0a00-0b00-0c00-0d0000000000 "Authorization:Token 5eceb05d00000000000000000000000000000000"
http GET http://127.0.0.1:8000/api/v1/tor_bridges/get_telegraf_config/ "Authorization:Token 5eceb05d00000000000000000000000000000000" port==9065
```

Telegraf Monitoring

```
curl -X GET -H 'Authorization: Token 5eceb05d00000000000000000000000000000000' 'http://localhost:8000/api/v1/tor_bridges/get_telegraf_config/?port=9065'
```

## Loose notes from original repo

pylightning <- Christian Decker (for lightningd (=c-lightning?!))

https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md
https://github.com/ElementsProject/lightning/tree/master/contrib/pylightning

switch on sites (in APPs and Site_id)

`lnnode` requires Redis (used to reduces external calls (e.g. getinfo) and improve performance)


ToDo

- Heartbeat / Check
- Maybe: validate/clean/save that models are only set to things the user owns
- AGBs/ToS
- loaddata did't work (caused by signal activity) - check again now that celery tasks are used.


https://github.com/jazzband/django-taggit/commit/90c7224018c941b9a260c8e8bed166536f5870df


pymacaroons

https://gist.github.com/htp/fbce19069187ec1cc486b594104f01d0


python manage.py migrate

Run on host to monitor

```
while :
do
  ./tor2ipc.sh list
  sleep 10
done
```
## SSL certificates for the Shop
### Generating SSL certificates for the first time
From the machine running the Shop, we can get the SSL certificates running the ```certbot``` with this command, and following the steps.
This will require that you have access to the domain ```<yourdomain>```, and that you add some dns entries in your domain management account.
In any case, if you run this command, it will tell you exactly what to do.
```
sudo certbot certonly --manual --email <your@email.com> --agree-tos --manual-public-ip-logging-ok --preferred-challenges=dns -d *.<yourdomain> -d <yourdomain>
```

Once the certificates have been generated, go to their location (usually ```/etc/letsencrypt/live/<yourdomain>```) and copy them to the folder in the Shop project ```/ssl/<yourdomain>```

### Renewing SSL certificates
The following command is the one to renew the certificates we generated in the Shop machine. Usually the renewal is performed (and allowed by ```certbot```) when the cert is close to its expiry date.
```
sudo certbot renew
```

## Backups
The file ```shop/tasks.py``` includes tasks to backup files and database and to delete old backups. The ```.env``` variable ```DELETE_OLD_BACKUPS_AFTER_DAYS``` can be set to how many days to keep backup files.
Also, these variables include a cron schedule for when to run each of those tasks:
```
SCHEDULE_BACKUP_FILES="0 12 * * *"
SCHEDULE_BACKUP_DB="30 23 * * *"
SCHEDULE_DELETE_OLD_BACKUPS="30 12 * * *"
```

## Updating settings without having to modify the repo (DEPRECATED)
At the moment, just go to the ip2tor/django_ip2tor/settings.py file and update as necessary.

Originally I designed this structure to patch the settings file with an editable copy at the .docker/patch folder.
There, you'll find the settings.py file, which will overwrite the one downloaded the repo, so you can update some stuff there if necessary without modifying the original settings file in the django folder.

You could still use this way if you prefer, but you'll have to add a line in the start.sh script:
```cp /home/ip2tor/.docker/patch/settings.py /home/ip2tor/ip2tor/django_ip2tor/settings.py```


# Open points

## The 'daphne' service
I still need to figure out what the service offered via 'daphne' was about, since all endpoints seem to work just fine without it.
In the meantime, the container offering it is commented out, so no 'daphne' server is loaded.
The nginx entry points to daphne are also commented out.