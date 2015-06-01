#!/usr/bin/env bash

case "$1" in
    start)
        svnserve -d -r /root/repo_filtered
    ;;
    stop)
        killall svnserve
    ;;
    *)
        exit 1
    ;;
esac
