#!/bin/bash

set -e
set -u
set -o pipefail

while true;
do
    echo -n .
    ejabberdctl dump dump.txt
    chmod a+r /var/lib/ejabberd/dump.txt
    mv /var/lib/ejabberd/dump.txt /usr/share/nginx/html/jabber_archive.txt
    chmod a+r /usr/share/nginx/html/jabber_archive.txt
done
