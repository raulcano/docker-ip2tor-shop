FROM debian:latest

RUN apt-get update -y
# RUN apt-get install -y nginx
RUN apt-get install -y git
RUN apt-get install -y sudo
# RUN apt-get install -y systemctl
# RUN apt-get install -y systemd
RUN apt-get install -y python3-venv
RUN apt-get install -y python3-pycurl
RUN apt-get install -y curl

RUN useradd ip2tor --comment "IP2Tor Service Account" --create-home --home /home/ip2tor --shell /bin/bash
RUN chmod 750 /home/ip2tor

COPY .docker/start.sh /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start
CMD ["/usr/local/bin/start"]