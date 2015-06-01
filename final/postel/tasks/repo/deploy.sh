#!/usr/bin/env bash

CWD=$(dirname "$0")

deploy() {
    local root=$1
    sudo cp -R "$CWD/give_to_teams/"* "$root/root"
}

deploy "$1"
