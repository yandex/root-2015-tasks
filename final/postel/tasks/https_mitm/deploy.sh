#!/usr/bin/env bash

CWD=$(dirname "$0")

deploy() {
    local root=$1
    sudo cp "$CWD/mitm."{key,crt} "$root/root"
}

deploy "$1"
