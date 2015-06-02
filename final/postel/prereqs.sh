#!/usr/bin/env bash

install_pkgs() {
    local pkgs=(
        apt-file
        binutils
        debootstrap
        dnsutils
        kpartx
        make
        moreutils
        openssl
        parted
        python2.7
        python-git
        python-paramiko
        python3
        python3-pil
        python3-requests
        subversion
        wget
        yum
    )
    sudo apt-get -y install "${pkgs[@]}"
}

setup_netflow() {
    local name=dpkt-1.6 cwd=$(dirname "$0") tmp=$(mktemp -d)
    tar -C "$tmp" -x -f "$cwd/tasks/netflow/${name}.tar"
    make -C "$tmp/$name" && sudo make -C "$tmp/$name" install
    rm -rf "$tmp"
}

setup_vbox_networking() {
    local ifname=$VM_HOST_INTERFACE ifip=192.168.26.1
    local vbm=(sudo VBoxManage)
    if ! "${vbm[@]}" list hostonlyifs | grep "$ifname" >/dev/null; then
        "${vbm[@]}" hostonlyif create
    fi
    "${vbm[@]}" hostonlyif ipconfig "$ifname" --ip "$ifip"
}

source "$(dirname "$0")/config.sh"

install_pkgs
setup_netflow

if [[ "$1" == "build" ]]; then
    setup_vbox_networking
fi
