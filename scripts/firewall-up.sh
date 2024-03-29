#!/bin/bash
# Firewall basic installation and config
echo "Installing the firewall and creating the basic config..."
sudo apt-get install -y ufw

# by default, we deny incoming traffic
sudo ufw default deny incoming

# by default, we allow outgoing traffic 
sudo ufw default allow outgoing

# we allow http,  https and 9050
sudo ufw allow http
sudo ufw allow https
sudo ufw allow ssh
sudo ufw allow 22
sudo ufw allow OpenSSH
sudo ufw allow 9050

# the sample hidden service port
sudo ufw allow 8333

# to allow postgres port - by default is blocked since it does not needed to be exposed
# need to allow traffic if we want to query the db directly from the outside
# sudo ufw allow 5432

sudo ufw enable
