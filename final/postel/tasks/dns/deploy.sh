#!/usr/bin/env bash

CWD=$(dirname "$0")

deploy() {
    local root=$1
    sudo cp "$CWD/dns.hosts" "$root/root"
}

deploy "$1"
