#!/usr/bin/env bash

CWD=$(dirname "$0")
PWD=root.yandex.com

KEY="$CWD/mitm.key"
CSR="$CWD/mitm.csr"
CRT="$CWD/mitm.crt"

openssl genrsa -passout pass:"$PWD" -des3 -out "$KEY" 1024
openssl req -new -config "$CWD/openssl.conf" -key "$KEY" \
    -out "$CSR" -passin pass:"$PWD"
mv -f "$KEY" "${KEY}.orig"
openssl rsa -in "${KEY}.orig" -out "$KEY" -passin pass:"$PWD"
rm "${KEY}.orig"
openssl x509 -req -days 365 -in "$CSR" -signkey "$KEY" -out "$CRT"
