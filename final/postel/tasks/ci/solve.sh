#!/usr/bin/env bash

CWD=$(dirname "$0")

INDIANA=${INDIANA_IP:?plese specify the IP of OpenIndiana image in \$INDIANA_IP}
PRIVKEY="$CWD/id_rsa"

chmod 600 "$PRIVKEY"
SSH_OPTS=(-o GlobalKnownHostsFile=/dev/null
          -o UserKnownHostsFile=/dev/null
          -o StrictHostKeyChecking=no
          -i "$PRIVKEY")
SSH=(ssh "${SSH_OPTS[@]}" "root@$INDIANA")
SCP=(scp "${SSH_OPTS[@]}")

solve() {
    local root=$1
    local inside=(sudo chroot "$root")
    local apt_get=("${inside[@]}" apt-get -y)

    "${apt_get[@]}" update; "${apt_get[@]}" install apt-transport-https

    sudo cp "$CWD/docker.list" "$root/etc/apt/sources.list.d"
    "${inside[@]}" apt-key adv \
        --keyserver 'hkp://keyserver.ubuntu.com:80' \
        --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9

    "${apt_get[@]}" update; "${apt_get[@]}" install \
        curl openssh-server lxc-docker nginx

    "${inside[@]}" mkdir -p /root/.ssh
    cat "$CWD/id_rsa.pub" | "${inside[@]}" bash -c \
        'umask 177; cat >> /root/.ssh/authorized_keys'

    sed "s/INDIANA/$INDIANA/" "$CWD/ci.conf" |
        "${inside[@]}" cp /dev/stdin /etc/nginx/sites-enabled/ci.conf

    "${inside[@]}" docker pull elyase/staticpython

    for service in ssh docker nginx; do
        "${inside[@]}" "/etc/init.d/$service" stop
    done

    "${inside[@]}" bash -c 'umount /sys/fs/cgroup/* /sys/fs/cgroup'
    sudo "${SCP[@]}" -r "root@$INDIANA:app.git" "$root/root/"
}

configure_indiana() {
    local target=$1
    local config=$(mktemp)

    sed "s/<\$SERVER_DOCKER>/$target/" "$CWD/config.xml" > "$config"
    curl -XPOST "http://${INDIANA}:8080/hudson/job/serverMVC_docker/doDelete"
    curl -L -s -XPOST --data-binary "@$config" -H 'Content-Type:text/xml' \
        "http://${INDIANA}:8080/hudson/createItem?name=serverMVC_docker"
    rm "$config"

    "${SSH[@]}" mkdir -p .ssh
    echo 'StrictHostKeyChecking no' | "${SSH[@]}" "cat > .ssh/config"
    "${SSH[@]}" ssh-keygen -R "$target"
    "${SCP[@]}" "$CWD/id_rsa" "root@$INDIANA:.ssh/id_rsa"
}

solve "$1"
configure_indiana "$2"
