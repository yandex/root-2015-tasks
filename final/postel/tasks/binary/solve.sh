#!/usr/bin/env bash

CWD=$(dirname "$0")

find_infected_binary() {
    local root=$1
    declare -A sums
    while read sum file; do
        sums[$root/$file]=$sum
    done < <(cat "$root/var/lib/dpkg/info/"*.md5sums)
    find "$root" -executable 2>/dev/null | while read binary; do
        if ! [[ -z "${sums[$binary]}" ]] &&
             [[ "${sums[$binary]}" != "$(md5sum "$binary" | cut -f1 -d' ')" ]]; then
            echo "$binary"
        fi
    done
}

find_package() {
    local root=$1 binary=${2/[/\\[}
    local db=$(mktemp -d)
    local apt_file=(apt-file -c "$db" -s "$root/etc/apt/sources.list")
    "${apt_file[@]}" update >/dev/null
    "${apt_file[@]}" --package-only -x find "^${binary}$"
    rm -rf "$db"
}

solve() {
    local root=${1%/} target=/usr/share/nginx/www/binary.txt
    local inside=(sudo chroot "$root")
    local apt_get=("${inside[@]}" apt-get -y --no-install-recommends)

    binary=$(find_infected_binary "$root")
    package=$(find_package "$root" "${binary##$root}")

    infected="${binary}.infected"
    sudo mv "$binary" "$infected"

    # If this fails, then this was a very sensitive binary, and we need another
    # solution which restores the image via deboostrap in a separate root,
    # for example.
    "${apt_get[@]}" update
    "${apt_get[@]}" install --reinstall "$package"

    # The answer and the target path are to be found manually by looking at the
    # diff. Luckily, this is fairly straightforward. Here in a script we just
    # simulate "smart lookup".
    sudo strip "$infected"
    message=$(diff <(strings -n10 "$binary") <(strings -n10 "$infected") |
              grep 'This is it.')
    answer=$(cut -f2 -d\' <<<"$message")

    "${apt_get[@]}" install nginx
    "${inside[@]}" /etc/init.d/nginx stop
    echo "$answer" | "${inside[@]}" cp /dev/stdin "$target"
    "${inside[@]}" chown www-data: "$target"
}

solve "$1"
