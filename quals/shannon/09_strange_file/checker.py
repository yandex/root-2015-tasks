#!/usr/bin/env python3

import sys
import os
import re
import signal
import subprocess

# CONSTS
OK = 10
NOTOK = 11
CHECKERERROR = 100

TIMEOUT = 20

SSH_ARGS = ["ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "CheckHostIP=no",
            "-o", "NoHostAuthenticationForLocalhost=yes",
            "-o", "BatchMode=yes",
            "-o", "LogLevel=ERROR",
            "-o", "UserKnownHostsFile=/dev/null",
            "-l", "tester"]


INODES = set((2228232, 2228236))

def check_inode(ip):
    p = subprocess.Popen(SSH_ARGS + ["-i", "key", ip, "ls -i file"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = p.stdout.read().decode("utf-8")
    try:
        inode = int(output.split()[0])
    except IndexError:
        print("404")
        sys.exit(NOTOK)
    if inode not in INODES:
        print("You are cheating!")
        print("Inode {0} != {1}".format(inode, INODES), file=sys.stderr)
        sys.exit(NOTOK)

    status = p.wait()


def check_file_update(ip):
    p = subprocess.Popen(SSH_ARGS + ["-i", "key", ip, "echo Hello! >> file"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = str(p.stdout.read())
    output_err = p.stderr.read().decode("utf-8").strip()
    status = p.wait()

    if status != 0:
        print(output_err)
        print(output, file=sys.stderr)
        print(output_err, file=sys.stderr)
        sys.exit(NOTOK)


def check(ip):
    check_inode(ip)
    check_file_update(ip)

    print("OK")
    sys.exit(OK)


if __name__ == "__main__":
    signal.alarm(TIMEOUT)

    if len(sys.argv) < 2:
        print("Usage: ./checker.py <ip>")
        sys.exit(CHECKERERROR)

    # cd to script directory
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    ip = sys.argv[1]
    check(ip)
