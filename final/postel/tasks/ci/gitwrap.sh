#!/bin/bash

CWD=$(dirname "$0")

ssh -i $CWD/id_rsa -o StrictHostKeyChecking=no -o CheckHostIP=no -o NoHostAuthenticationForLocalhost=yes -o BatchMode=yes -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null $@
