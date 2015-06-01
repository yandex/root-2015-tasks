#!/usr/bin/env bash

for subj in astronomy geology gyroscope literature marketing \
            mathematics music polit agrobiologia law psychology \
            geography physics philosophy chemistry estetica; do
    mkdir -p "$subj"
    for i in {1..100}; do
        wget -O "$subj/$i.html" "http://referats.yandex.ru/referats/?t=$subj&s=$i"
        sleep 1
    done
done
