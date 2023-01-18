#!/bin/bash
# Firewall basic installation and config
echo "Installing the firewall and creating the basic config..."
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow http
sudo ufw allow https
sudo ufw allow ssh
sudo ufw allow 22
sudo ufw allow OpenSSH
sudo ufw allow 9050
# the sample hidden service port
sudo ufw allow 8333
sudo ufw enable
