# Dockerfile for the Tor hidden service
FROM debian:latest

RUN apt-get update -y
RUN apt-get install -y sudo
RUN apt-get install -y python3
RUN apt-get install -y pip

RUN python3 -m pip install python-dotenv

COPY .env /usr/share/.env
COPY .docker/sample-hidden-service/serve-page.py /usr/share/serve-page.py
COPY .docker/sample-hidden-service/index.html /usr/share/index.html

COPY .docker/sample-hidden-service/sample-http-start.sh /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start
CMD ["/usr/local/bin/start"]