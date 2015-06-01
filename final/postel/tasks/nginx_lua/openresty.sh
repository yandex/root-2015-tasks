#!/usr/bin/env bash

NAME=/usr/local/openresty/nginx/sbin/nginx

case "$1" in
    start) "$NAME" ;;
    stop)  killall "$NAME" ;;
    *)     exit 1 ;;
esac
