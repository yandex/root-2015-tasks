#!/usr/bin/env bash

CWD=$(dirname "$0")

solve() {
    local root=$1
    local inside=(sudo chroot "$1")
    local apt_get=("${inside[@]}" apt-get)

    local deps=(nginx screen)
    local apt_opts=(-y --no-install-recommends)

    local deps_backports=(yum createrepo python-deltarpm python2.7 sed)
    local apt_opts_backports=("${apt_opts[@]}" -t wheezy-backports)


    sudo cp "$CWD/backports.list" "$root/etc/apt/sources.list.d"

    "${apt_get[@]}" update
    "${apt_get[@]}" "${apt_opts[@]}" install "${deps[@]}"
    "${apt_get[@]}" "${apt_opts_backports[@]}" install "${deps_backports[@]}"
    "${inside[@]}" /etc/init.d/nginx stop

    sudo cp -R "$CWD/mergerepo" "$root/root"
    "${inside[@]}" sed -i -e 's@</repomd>@\
            <data type="other"><location href="nonexists"/></data></repomd>@' \
        /root/repo/repodata/repomd.xml

    "${inside[@]}" bash -c 'cd /root &&
        screen -dm -S webserver python -m SimpleHTTPServer 8000'
    "${inside[@]}" bash -c ' cd /root/mergerepo && python2 ./mergerepo.py \
        --repo=http://localhost:8000/repo --repo=http://localhost:8000/repo'

    sudo mkdir -p "$root/usr/share/nginx/www/"
    "${inside[@]}" mv /root/mergerepo/merged_repo /usr/share/nginx/www/repo
    "${inside[@]}" chmod a+rX -R /usr/share/nginx/www/repo

    "${inside[@]}" screen -X -S webserver quit
}

solve "$1" "$2"
