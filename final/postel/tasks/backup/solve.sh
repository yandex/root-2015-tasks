#!/usr/bin/env bash

solve() {
    local root=$1
    local inside=(sudo chroot "$root")
    "${inside[@]}" apt-get update
    "${inside[@]}" apt-get -y --no-install-recommends install nginx
    "${inside[@]}" /etc/init.d/nginx stop

    key=$(sudo head -n1 "$root/root/.bash_history" |
          perl -ne"/pass:(.+?)\'/ && print \$1")
    backups=("$root/var/backups"/*encrypted)
    for i in $(seq "${#backups[@]}" -1 1); do
        local dst="${backups[i-1]}.extracted"
        sudo mkdir -p "$dst"
        lastkey=$key
        key=$(sudo cat "${backups[i-1]}" |
              openssl aes-128-cbc -d -pass "pass:$lastkey" |
              tar xzf - -O root/backup.key)
        sudo cat "${backups[i-1]}" |
            openssl aes-128-cbc -d -pass "pass:$lastkey" |
            sudo tar xzf - -C "$dst"
    done

    local prefix=usr/share/nginx/www/referats
    sudo mkdir -p "$root/$prefix"
    for backup in "${backups[@]}"; do
        sudo cp -R "${backup}.extracted/$prefix/"* "$root/$prefix"
    done
}

solve "$1"
