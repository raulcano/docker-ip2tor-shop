#!/bin/sh

ps aux | grep gunicorn | grep django_ip2tor | awk '{ print $2 }' | xargs kill -HUP