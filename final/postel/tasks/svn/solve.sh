#!/usr/bin/env bash

CWD=$(dirname "$0")

solve() {
    local root=$1
    local inside=(sudo chroot "$1")

    sudo cp "$CWD/backports.list" "$root/etc/apt/sources.list.d"
    "${inside[@]}" apt-get update
    "${inside[@]}" apt-get -y --no-install-recommends -t wheezy-backports \
        install subversion

    "${inside[@]}" mkdir /root/repo_filtered
    "${inside[@]}" svnadmin create /root/repo_filtered
    "${inside[@]}" svnadmin dump /root/repo |
        "$CWD/svndump_filter.py" |
        "${inside[@]}" svnadmin load /root/repo_filtered

    sudo cp "$CWD/serve.sh" "$root/etc/init.d/svnserve.sh"
    "${inside[@]}" update-rc.d -f svnserve.sh defaults
}

solve "$1"
