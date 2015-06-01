#!/usr/bin/env bash

CWD=$(dirname "$0")
KDC_IP=${NFS_SERVER_IP:-10.10.10.11}

esc() {
    printf "%q" "$1"
}

solve() {
    local root=$1
    local inside=(sudo chroot "$root")
    "${inside[@]}" apt-get update
    "${inside[@]}" bash -c 'export DEBIAN_FRONTEND=noninteractive
        apt-get -y --no-install-recommends install nfs-common krb5-user nginx'
    "${inside[@]}" /etc/init.d/nginx stop
    "${inside[@]}" /etc/init.d/nfs-common stop
    sudo fuser -k "$root"

    local default=/etc/default/nfs-common conf=/etc/krb5.conf
    sudo bash -c "echo NEED_GSSD=yes >> $(esc "$root$default")"
    sudo bash -c "echo RPCGSSDOPTS='-n' >> $(esc "$root$default")"
    sed "s/KDC_IP/$KDC_IP/" "$CWD/${conf##*/}" | "${inside[@]}" cp /dev/stdin "$conf"
    "${inside[@]}" chmod 644 "$conf"

    sudo bash -c "echo '$KDC_IP localhost' > $(esc "$root/etc/hosts")"

    local target=/usr/share/nginx/www/nfs
    "${inside[@]}" mkdir -p "$target"
    "${inside[@]}" chown www-data: "$target"

    local initscript=/etc/init.d/yaroot-mount-nfs.sh
    sudo cp "$CWD/mount.sh" "$root$initscript"
    sudo chmod 700 "$root$initscript"
    "${inside[@]}" update-rc.d -f "${initscript##*/}" defaults
}

solve "$1"
