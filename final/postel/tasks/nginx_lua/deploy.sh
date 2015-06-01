#!/usr/bin/env bash

set -x

CWD=$(dirname "$0")

deploy() {
    local root=$1
    local inside=(sudo chroot "$root")
    
    "${inside[@]}" apt-get update
    "${inside[@]}" apt-get -y --force-yes install nginx

    sudo mkdir -p "$root/etc/nginx/lua"
    "${inside[@]}" chown www-data:www-data -R "/etc/nginx/lua"
    sudo cp "$CWD"/task_sources/*.lua "$root/etc/nginx/lua/"

    sudo mkdir -p "$root/var/www/static"
    "${inside[@]}" chown www-data:www-data -R "/var/www"
    sudo cp "$CWD"/static/* "$root/var/www/static"
}

deploy "$1"
