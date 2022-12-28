# Dockerfile for the Tor hidden service
FROM debian:latest

RUN apt-get update -y
RUN apt-get install -y sudo
RUN apt-get install -y tor

ARG ONION_PORT
ARG HTTP_PORT

RUN echo "HiddenServiceDir /var/lib/tor/sample_hidden_service/" | sudo tee --append /etc/tor/torrc
# see this https://www.freecodecamp.org/news/how-to-get-a-docker-container-ip-address-explained-with-examples/
# using the hostname of the corresponding service
RUN echo "HiddenServicePort $ONION_PORT sample-http:$HTTP_PORT" | sudo tee --append /etc/tor/torrc

COPY .docker/sample-hidden-service/sample-hidden-service-start.sh /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start
ENTRYPOINT ["/bin/sh", "/usr/local/bin/start"]
CMD ["tor"]