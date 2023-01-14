#!/bin/bash

source /home/ip2tor/ip2tor/.env

echo 'Deleting old backup files...'
find /home/ip2tor/backups/* -type f -mtime +${DELETE_OLD_BACKUPS_AFTER_DAYS}
find /home/ip2tor/backups/* -type f -mtime +${DELETE_OLD_BACKUPS_AFTER_DAYS} | xargs rm -f