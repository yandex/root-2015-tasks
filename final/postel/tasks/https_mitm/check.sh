#!/usr/bin/env bash

CWD=$(dirname "$0")
CURL=(curl -m 5 --max-redirs 0)

ATTEMPTS=5
GET_ATTEMPTS=5
SIGNATURE=root.yandex.com

get_host() {
    local data="$CWD/hosts.ok"
    local size=$(wc -l "$data" | cut -f1 -d' ')
    for i in $(seq "$GET_ATTEMPTS"); do
        local line=$(python -c'
import random, sys
print random.randrange(int(sys.argv[1]))' "$size")
        local host=$(head -n "$line" "$data" | tail -n1)
        if "${CURL[@]}" -D /dev/stdout -o /dev/null "https://$host/" |
                grep -q -i '^Server:'; then
            echo "$host"
            return
        fi
    done
}

check() {
    local address=$1 ok=0
    for i in $(seq "$ATTEMPTS"); do
        local host=$(get_host)
        if ! [[ -z "$host" ]] && "${CURL[@]}" -x "http://$address:3129/" \
                -o /dev/null -D /dev/stdout \
                --cacert "$CWD/mitm.crt" "https://$host/" |
                grep -i '^Server:' | grep -q "$SIGNATURE"; then
            ((++ok))
        fi
    done
    if [[ "$ok" -lt "$((ATTEMPTS-1))" ]]; then return 11; else return 10; fi
}

check "$1"
