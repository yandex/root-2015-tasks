#!/usr/bin/env bash

CWD=$(dirname "$0")
CURL=(curl -m 5 --max-redirs 0)
STRING='v3249f78h3p49fh'

check() {
    local host=$1
    if "${CURL[@]}" "http://$host/binary.txt" | grep "$STRING" >/dev/null; then
        return 10
    else
        return 11
    fi
}

check "$1"
