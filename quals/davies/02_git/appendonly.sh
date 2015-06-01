#!/bin/bash
#
# --- Command line
refname="$1"
oldrev="$2"
newrev="$3"

# --- Safety check
if [ -z "$GIT_DIR" ]; then
    echo "Don't run this script from the command line." >&2
    echo " (if you want, you could supply GIT_DIR then run" >&2
    echo "  $0 <ref> <oldrev> <newrev>)" >&2
    exit 1
fi

if [ -z "$refname" -o -z "$oldrev" -o -z "$newrev" ]; then
    echo "usage: $0 <ref> <oldrev> <newrev>" >&2
    exit 1
fi

diff=$(git diff $oldrev $newrev)

if echo "$diff" | grep -vE "^\-\-\-" | grep -E "^\-" > /dev/null 2>&1; then
    echo "*** Found deletion/modification! This repository is append-only! ***" >&2
    exit 1
else
    numered_diff=$(echo "$diff" | grep -vE "^\+{3}" | grep -nE "^(\+|diff| )" | tail -n +2)
    prev=$(echo "$numered_diff" | grep -E ":\+" | head -n 1 | cut -d ':' -f 1)
    numered_diff=$(echo "$numered_diff" | tail -n +$(echo "$numered_diff" | grep -nE ":\+" | head -n 1 | cut -d ':' -f 1) | tail -n +2)
    new_diff=1
    while read LINE; do
        curr=$(echo $LINE | cut -d ':' -f 1)
        if echo $LINE | grep -E ": " > /dev/null 2>&1; then
            if [[ $((prev + 1)) -eq $curr  ]]; then
                echo "*** Found modification not in the tail of file. This repository is append-only! ***" >&2
                exit 1
            else
                continue
            fi
        fi
        #echo $prev $curr $LINE
        if echo $LINE | grep -E ":diff --git" > /dev/null 2>&1; then
            if [[ $((prev + 1)) -ne $curr  ]]; then
                echo "*** Found modification not in the tail of file. This repository is append-only! ***" >&2
                exit 1
            fi
            new_diff=0
        else
                if [[ $((prev + 1)) -ne $curr  ]]; then
                   if [[ -n $new_diff ]]; then
                        new_diff=1
                    fi
                fi
        fi
        if echo $LINE | grep -E ":\+" > /dev/null 2>&1; then
            prev=$curr
        fi
    done <<< "$numered_diff"
fi
