#!/usr/bin/env bash

install_pkgs() {
    local pkgs=(
        python3
        python
        python-paramiko
        python-requests
        python-git
        python-gitdb
        python-couchdb
        python-dnspython
        python-jabberbot
        libsctp1
        python-crypto
    )
    sudo apt-get -y install "${pkgs[@]}"
}

install_pkgs
