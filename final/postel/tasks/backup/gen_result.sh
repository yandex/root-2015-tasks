#!/usr/bin/env bash

CWD=$(dirname "$0")
RND="$CWD/rnd.py"

generate() {
    local iters=100
    declare -A result
    for i in $(seq "$iters"); do
        while read -r -d '' filename; do
            subj=${filename%%/*}
            number=${filename##*/}
            result[$subj]=$number
        done < <("$RND" files "$i")
    done

    for subj in "${!result[@]}"; do
        echo "$subj ${result[$subj]}";
    done > "$CWD/result.txt"
}

generate
