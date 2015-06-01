#!/usr/bin/bash

check() {
    local host="$1"
    if curl -m 10 -X HEAD -D /dev/stdout -o /dev/null "https://$host/" |
            grep -q -i '^Server:'; then
        touch "$host"
    fi
}

check "$1"
