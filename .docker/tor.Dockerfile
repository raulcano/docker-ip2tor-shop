# Dockerfile for the Tor hidden service
FROM debian:latest

RUN apt-get update -y
RUN apt-get install -y sudo
RUN apt-get install -y tor

RUN echo "HiddenServiceDir /var/lib/tor/ip2tor-shop_hidden_service/" | sudo tee --append /etc/tor/torrc


ARG SHOP_TOR_HTTP_PORT
ARG SHOP_TOR_HTTPS_PORT
ARG SHOP_CLEARNET_HTTP_PORT
ARG SHOP_CLEARNET_HTTPS_PORT
# see this https://www.freecodecamp.org/news/how-to-get-a-docker-container-ip-address-explained-with-examples/
# using the hostname of the corresponding service
RUN echo "HiddenServicePort ${SHOP_TOR_HTTP_PORT} nginx:${SHOP_TOR_HTTP_PORT}" | sudo tee --append /etc/tor/torrc
# RUN echo "HiddenServicePort ${SHOP_TOR_HTTPS_PORT} nginx:${SHOP_CLEARNET_HTTPS_PORT}" | sudo tee --append /etc/tor/torrc

COPY .docker/start-tor.sh /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start
ENTRYPOINT ["/bin/sh", "/usr/local/bin/start"]
CMD ["tor"]