#!/usr/bin/env bash

exec python "$(dirname "$0")/checker/repo.py" "$@"
