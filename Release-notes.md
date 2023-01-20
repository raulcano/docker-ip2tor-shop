Dockerized shop, with the following containers:
- Nginx
- Django gUnicorn
- Django Daphne
- Celery worker
- Celery beat
- Postgres
- Redis
- Tor
- Flower
- Sample HTTP service
- Sample Hidden service

New django commands:
- create host
- create operator
- create site
- create node
- ... and more under shop/management

Enhanced .env file and start script:
- Will create superuser
- Will create operator and add it to operators group
- Will create Site
- Will create LND  nodes from values in .env file.
- Will create hosts from values in the .env file
- Schedule of periodic tasks in env variables
- ... and much more variables in the .env file

Automatic testing:
- Hosts
- Purchase orders
- LND nodes
- Tor bridges

Tor hidden service for the Shop, optional, easily configurable.

A set of aliases for Shop and Host, useful for development.

Updates to class Host
- Allows the creation of multiple hosts instances with the same IP. This permits the definition of different prices and times (e.g. 24h service, 1 week service, etc.)

Updates to class PortRange
- Checks that port ranges do not overlap within the same host or within a host that has the same IP

Updates to class LndGrpcNode:
- Creates 'secure-channel' that will work if TLS verification is false (in effect is like an insecure channel)

Updates to PO
- PO creation: it won't create PO if there aren't ports available (it created the PO before with the port None)

Updates in Host
- Adds the 'sync' option to synchronize active bridges between the Shop and the Host. That is, this will remove any bridge in the Host that does not correspond to any active bridge in the Shop, and will add those bridges that are active in Shop but not in the Host.
- The Host docker container will open or close ports in the host machine with the ufw firewall based on the bridges that are active or not (this is done using a SSH connection from the docker container to the host).
- Allows more than 1 Host instance in the same IP, with the condition that Ports do not overlap and names be different. This allows for offering different prices /
 duration of the Tor Bridges in the same IP (e.g. 24h, 1 week, 1 month, etc.)
- All relevant logs are now in the same folder "logs", but in different files depending on the service and type of log (e.g. stdout vs. error).

Documentation
- Updated README file
- Created  a class diagram for clarity