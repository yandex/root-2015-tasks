#!/usr/bin/env bash

CWD=$(dirname "$0")

solve() {
    local root=$1
    local inside=(sudo chroot "$root")
    local apt_get=("${inside[@]}" apt-get -y --no-install-recommends)
    local deps=(perl perl-modules libmagickcore5 libmagick++5 libmagickwand5
                libmagickwand-dev)
    local bdeps=(make g++ libpcre++-dev libssl-dev libmagick++-dev)
    "${apt_get[@]}" update
    "${apt_get[@]}" install "${deps[@]}" "${bdeps[@]}"

    "${inside[@]}" bash -x -c '
        wget "http://openresty.org/download/ngx_openresty-1.7.10.1.tar.gz"
        tar zxf ngx_openresty-*
        cd ngx_openresty-*
        ./configure --with-luajit
        make -j32
        make install
        cd ..
        rm -rf ngx_openresty-*
    '

    local conf="$root/usr/local/openresty/nginx/conf"
    sudo mkdir -p "$conf/sites-available/" "$conf/sites-enabled/"
    sudo cp "$CWD/solution/nginx_server.conf" "$conf/sites-available/default"
    sudo ln -s "../sites-available/default" "$conf/sites-enabled/default"
    sudo cp "$CWD/solution/nginx.conf" "$conf/nginx.conf"

    sudo cp -R "$CWD/solution/magick" "$root/etc/nginx/lua/"
    sudo cp "$CWD/solution/magick.lua" "$root/etc/nginx/lua/"
    sudo cp "$CWD/task_sources/resize_image.lua.fixed" \
        "$root/etc/nginx/lua/resize_image.lua"

    "${inside[@]}" mkdir /var/www/cache
    "${inside[@]}" chown -R www-data: /var/www/cache
    sudo cp "$CWD/openresty.sh" "$root/etc/init.d"
    "${inside[@]}" update-rc.d -f openresty.sh defaults

    "${apt_get[@]}" purge "${bdeps[@]}"
    "${apt_get[@]}" --purge autoremove
    "${apt_get[@]}" clean
}

solve "$1"
