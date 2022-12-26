FROM debian:latest

RUN apt-get update -y
RUN apt-get install -y git
RUN apt-get install -y sudo
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN apt-get install -y python3-pycurl
RUN apt-get install -y curl
RUN apt-get install -y procps
RUN apt-get install -y iputils-ping
RUN apt-get install -y nano

RUN useradd ip2tor --comment "IP2Tor Service Account" --create-home --home /home/ip2tor --shell /bin/bash
RUN chmod 750 /home/ip2tor

# Install python dependencies
COPY .docker/requirements.txt /usr/share/requirements.txt
COPY .docker/restart-gunicorn.sh /usr/share/restart-gunicorn.sh
RUN chmod u+x /usr/share/restart-gunicorn.sh
RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install --upgrade -r /usr/share/requirements.txt
RUN python3 -m pip install --upgrade psycopg2-binary
RUN python3 -m pip install gunicorn
RUN python3 -m pip install flower

# These are for testing
RUN python3 -m pip install pytest
RUN python3 -m pip install pytest-django
RUN python3 -m pip install model_bakery

# RUN runuser -l ip2tor -c 'python3 -m pip install --upgrade pip setuptools'
# RUN runuser -l ip2tor -c 'python3 -m pip install --upgrade -r /usr/share/requirements.txt'
# RUN runuser -l ip2tor -c 'python3 -m pip install --upgrade psycopg2-binary'
# RUN runuser -l ip2tor -c 'python3 -m pip install pytest'
# RUN runuser -l ip2tor -c 'python3 -m pip install pytest-django'

COPY .docker/start.sh /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start
CMD ["/usr/local/bin/start"]