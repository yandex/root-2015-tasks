#!/usr/bin/env bash

CWD=$(dirname "$0")

ATTEMPTS=7
NORMAL="$CWD/../https_mitm/hosts"
MITM="$CWD/dns.hosts"

get_a() {
    local host=$1 dns=$2
    local dig=(dig +noauthority +noadditional +nocl +nottlid +time=5 +tries=1 -t A)
    if [[ -z "$dns" ]]; then
        "${dig[@]}" "$host"
    else
        "${dig[@]}" "$host" "@$dns"
    fi | grep -v '^;' | grep -v '^$' | sort
}

get_host() {
    local data=$1
    local size=$(wc -l "$data" | cut -f1 -d' ')
    local line=$(python -c'
import random, sys
print random.randrange(int(sys.argv[1]))' "$size")
    head -n "$line" "$data" | tail -n1
}

get_mitm_host() {
    get_host "$MITM"
}

get_normal_host() {
    while true; do
        local normal=$(get_host "$NORMAL")
        if ! grep -q "^$normal$" "$MITM"; then
            echo "$normal"
            return
        fi
    done
}

check() {
    local address=$1 ok=0
    for i in $(seq "$ATTEMPTS"); do
        local normal_host=$(get_normal_host) mitm_host=$(get_mitm_host)
        if cmp -s <(get_a "$normal_host") <(get_a "$normal_host" "$address") &&
            ! get_a "$mitm_host" | grep -q "$address" &&
              get_a "$mitm_host" "$address" | grep -q "$address"; then
            if [[ "$((++ok))" -eq "$((ATTEMPTS-2))" ]]; then
                return 10;
            fi
        fi
    done
    return 11
}

check "$1"
