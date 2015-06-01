#!/usr/bin/env bash

CWD=$(dirname "$0")

chmod 600 "$CWD/id_rsa"
exec "$CWD/checker.py" "$@"
