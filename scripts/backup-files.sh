#!/bin/bash

basepath="/home/ip2tor"
# What to backup. 
backup_files="${basepath}"
excluded_files_txt="${basepath}/scripts/excluded-from-backup.txt"

# Where to backup to.
dest="${basepath}/backups"

# Create archive filename.
day=$(date +%Y-%m-%d-%H:%M:%S)
archive_file="${day}_ip2tor-shop-files.tgz"

# Print start status message.
echo "Backing up $backup_files to $dest/$archive_file"
date
echo

# Backup the files using tar.
sudo tar czf $dest/$archive_file -X $excluded_files_txt $backup_files

# Print end status message.
echo
echo "Backup finished"
date

# Long listing of files in $dest to check file sizes.
ls -lh $dest