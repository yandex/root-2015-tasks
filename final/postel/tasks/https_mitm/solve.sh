#!/usr/bin/env bash

CWD=$(dirname "$0")

solve() {
    local root=$1
    local inside=(sudo chroot "$1")
    local apt_get=("${inside[@]}" apt-get -y)
    local deps=(squid-langpack ca-certificates)
    local bdeps=(dpkg-dev libssl-dev libecap2-dev)
    local apt_opts=(-y --no-install-recommends -t wheezy-backports)

    sudo cp "$CWD/backports.list" "$root/etc/apt/sources.list.d"

    "${apt_get[@]}" update
    "${apt_get[@]}" "${apt_opts[@]}" install "${deps[@]}" "${bdeps[@]}"
    "${apt_get[@]}" "${apt_opts[@]}" build-dep squid3

    "${inside[@]}" mkdir -p /etc/squid3
    cat "$CWD/squid.conf" | "${inside[@]}" cp /dev/stdin /etc/squid3/squid.conf

    "${inside[@]}" bash -c '
dir=$(mktemp -d)
cd "$dir"
apt-get -t wheezy-backports source squid3
cd squid3-*
echo -e "\nDEB_CONFIGURE_EXTRA_FLAGS += --enable-ssl --enable-ssl-crtd" \
    >> debian/rules
time dpkg-buildpackage -j32
dpkg -i --force-confold ../squid3-common_*.deb ../squid3_*.deb
/etc/init.d/squid3 stop
/usr/lib/squid3/ssl_crtd -c -s /var/lib/ssl_db
chown -R proxy: /var/lib/ssl_db
rm -rf "$dir"
'
    "${apt_get[@]}" purge "${bdeps[@]}"
    "${apt_get[@]}" --purge autoremove
    "${apt_get[@]}" clean

    sudo fuser -k "$root"
}

solve "$1" "$2"
