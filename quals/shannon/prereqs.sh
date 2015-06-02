#!/usr/bin/env bash

install_pkgs() {
    local pkgs=(
        python-enet
        python3
        python
        python-pymongo
        python-openssl
        curl
        mongodb-clients
        mercurial
        python-twisted
        python3-mysql.connector
    )
    sudo apt-get -y install "${pkgs[@]}"
}

install_pkgs
