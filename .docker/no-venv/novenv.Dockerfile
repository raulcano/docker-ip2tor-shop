FROM debian:latest

RUN apt-get update -y
# RUN apt-get install -y nginx
RUN apt-get install -y git
RUN apt-get install -y sudo
# RUN apt-get install -y systemctl
# RUN apt-get install -y systemd
RUN apt-get install -y python3
RUN apt-get install -y pip
# RUN apt-get install -y python3-venv
RUN apt-get install -y python3-pycurl
RUN apt-get install -y curl

RUN useradd ip2tor --comment "IP2Tor Service Account" --create-home --home /home/ip2tor --shell /bin/bash
RUN chmod 750 /home/ip2tor

# From start.sh script
RUN sudo su - ip2tor
# RUN /usr/bin/python3 -m venv --system-site-packages /home/ip2tor/venv
# RUN source /home/ip2tor/venv/bin/activate

RUN python3 -m pip install --upgrade pip setuptools

# Get the codefrom Github
RUN mkdir /home/ip2tor/ip2tor
RUN git clone https://github.com/raulcano/ip2tor ip2tor

# Install python dependencies
RUN cd /home/ip2tor/ip2tor

# Add concrete version of Protobuf to requirements to avoid failure (we add the line if it does not exist)
RUN grep -qxF 'protobuf==3.20.*' requirements.txt || echo 'protobuf==3.20.*' >> requirements.txt
RUN grep -qxF 'daphne' requirements.txt || echo 'daphne' >> requirements.txt
RUN python3 -m pip install --upgrade -r requirements.txt
RUN python3 -m pip install --upgrade psycopg2-binary

COPY .docker/no-venv/start2.sh /usr/local/bin/start
RUN chmod u+x /usr/local/bin/start
CMD ["/usr/local/bin/start"]