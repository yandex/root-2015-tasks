#!/usr/bin/env bash

TARGET=/usr/share/nginx/www/nfs

do_mount() {
    local passwd=password
    kinit user <<<"$passwd"
    mount.nfs4 localhost:/dir "$TARGET" -o tcp,sec=krb5i
    su www-data -c "kinit user" <<<"$passwd"
}

case "$1" in
    start)
        do_mount
    ;;
    stop)
        umount "$TARGET"
    ;;
    *)
        exit 1
    ;;
esac
