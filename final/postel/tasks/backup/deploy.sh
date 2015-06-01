#!/usr/bin/env bash

CWD=$(dirname "$0")
RND="$CWD/rnd.py"

TMP=
cleanup() {
    if ! [[ -z "$TMP" ]]; then
        rm -rf "$TMP"
    fi
}

esc() {
    printf "%q" "$1"
}

deploy() {
    local root=$1
    local backups="$root/var/backups"
    mkdir -p "$backups"

    trap cleanup RETURN
    TMP=$(mktemp -d)

    local dst="$TMP/usr/share/nginx/www/referats"
    local iters=100
    for i in $(seq "$iters"); do
        mkdir -p "$dst"
        while read -r -d '' filename; do
            subj=${filename%%/*}
            cp "$CWD/data/referats/${filename}.txt" "$dst/${subj}.txt"
        done < <("$RND" files "$i")
        if [[ "$i" -eq 1 ]]; then
            cp "$CWD/data/referats/index.txt" "$dst/"
        fi

        mkdir -p "$TMP/root"
        "$RND" key "$((i-1))" > "$TMP/root/backup.key"
        filename="$backups/$("$RND" date "$i").tgz.encrypted"
        key=$("$RND" key "$i")
        ( cd "$TMP"; tar czf - *; ) |
            openssl aes-128-cbc -pass "pass:$key" |
            sudo bash -c "cat > $(esc "$filename")"
        sudo chown root: "$filename"
        sudo chmod 600 "$filename"
        rm -rf "$TMP"/*
    done
    sudo chown -R root: "$backups"

    sudo mkdir -p "$root/root"
    sudo bash -c "echo 'export HISTSIZE=10' >> $(esc "$root/root/.profile")"
    sudo bash -c "cat > $(esc "$root/root/.bash_history")" << END
tar cz -f - -C / root/backup.key usr/share/nginx/www/referats/ | \
openssl aes-128-cbc -pass 'pass:$("$RND" key "$iters")' > \
/var/backups/$("$RND" date "$iters").tgz.encrypted
rm -rf /
rm -rf /usr
killall5 -KILL
top
shutdown
init 0
reboot
echo b > /proc/sysrq-trigger
dd if=/dev/zero of=/dev/sda
END
    rm -rf "$TMP"; TMP=
}

deploy "$1"
