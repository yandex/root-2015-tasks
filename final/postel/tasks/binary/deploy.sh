#!/usr/bin/env bash

CWD=$(dirname "$0")

deploy() {
    local root=$1
    local inside=(sudo chroot "$root")
    local apt_get=("${inside[@]}" apt-get -y --no-install-recommends)
    sudo cp "$CWD/src.list" "$root/etc/apt/sources.list.d"
    "${apt_get[@]}" update
    "${apt_get[@]}" install dpkg-dev
    "${apt_get[@]}" build-dep coreutils
    sudo cp "$CWD/test.patch" "$root/tmp"
    "${inside[@]}" bash -c '
        tempdir=$(mktemp -d)
        cd "$tempdir"
        apt-get source coreutils
        cd coreutils-*
        debian/rules configure
        make -j32
        patch src/test.c < /tmp/test.patch
        rm /tmp/test.patch
        make -C src [
        cp ./src/[ /usr/bin
        cd /
        rm -rf "$tempdir"
    '
}

deploy "$1"
