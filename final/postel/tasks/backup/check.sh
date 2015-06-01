#!/usr/bin/env bash

CWD=$(dirname "$0")
CURL=(curl -m 5 --max-redirs 0)

check_one() {
    local file=$1 url=$2
    set -o pipefail
    "${CURL[@]}" "$url" | cmp -s - "$file"; rv=$?
    set +o pipefail
    if [[ "$rv" -ne 0 ]]; then
        exit 11
    fi
}

check() {
    local host=$1
    declare -A result
    while read subj number; do
        result[$subj]=$number
    done < "$CWD/result.txt"

    check_one "$CWD/data/referats/index.txt" "$host/referats/index.txt"

    for subj in "${!result[@]}"; do
        check_one "$CWD/data/referats/$subj/${result[$subj]}.txt" \
                  "http://$host/referats/${subj}.txt"
    done

    exit 10
}

check "$1"
