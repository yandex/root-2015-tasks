#!/usr/bin/env bash

CWD=$(dirname "$0")

inside() {
    local root=$1; shift
    sudo chroot "$root" "$@"
}

put() {
    local root=$1 src=$2 dst=$3 mode=$4
    inside "$root" mkdir -p "$dst"
    inside "$root" bash -c "cat > $(printf "%q" "$dst/$src")" < "$CWD/$src"
    inside "$root" chmod "$mode" "$dst/$src"
}

solve() {
    local root=$1
    inside "$root" apt-get update
    inside "$root" apt-get -y install flow-tools nginx
    inside "$root" /etc/init.d/nginx stop

    put "$root" flow.acl /root/nflow 600
    put "$root" report.conf /root/nflow 600
    put "$root" get_stat.sh /root/nflow 700
    put "$root" flow /etc/cron.d 600
    put "$root" flow-capture.conf /etc/flow-tools 600
    inside "$root" mkdir -p /var/nflow
}

solve "$@"
