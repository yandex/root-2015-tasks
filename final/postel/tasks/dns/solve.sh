#!/usr/bin/env bash

CWD=$(dirname "$0")

solve() {
    local root=$1 address=$2
    local inside=(sudo chroot "$1")
    "${inside[@]}" apt-get update
    "${inside[@]}" apt-get -y --no-install-recommends install bind9
    "${inside[@]}" /etc/init.d/bind9 stop
    for zone in $(sudo sort "$root/root/dns.hosts" | uniq); do
        local zonefile="/etc/bind/db.$zone"
        sed "s|ADDRESS|$address|;s|ZONE|$zone|" "$CWD/db.template" |
            "${inside[@]}" cp /dev/stdin "$zonefile"
        sudo chmod 644 "$root$zonefile"
        sed "s|ZONE|$zone|;s|FILE|$zonefile|" "$CWD/bind.conf.template"
    done | "${inside[@]}" cp /dev/stdin /etc/bind/named.conf.local
    sudo cp "$CWD/default" "$root/etc/default/bind9"
    sudo /etc/init.d/bind9 start
}

solve "$1" "$2"
