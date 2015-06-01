#!/usr/bin/env python2

import sys
import os
import signal
import traceback
import requests
import re

# CONSTS
OK = 10
NOTOK = 11
CHECKERERROR = 100

NFS_SERVER_IP = os.environ.get("NFS_SERVER_IP", "10.10.10.11")

TIMEOUT = 30

def alarm_handler(signum, frame):
    print("Timeout")
    sys.exit(NOTOK)

def check(ip):
    if "\n" in ip:
        print("Wrong IP")
        sys.exit(CHECKERERROR)

    # Put some file on nfs server
    try:
        resp = requests.get("http://%s/cgi-bin/putfile.py" % NFS_SERVER_IP)
        text = resp.text.strip()
    except Exception as E:
        print("NFS server is down")
        sys.exit(CHECKERERROR)

    m = re.search("(\w+):(\w+)", text)
    if not m:
        print("Unexpected answer from NFS server")
        sys.exit(CHECKERERROR)

    filename = m.group(1)
    contents = m.group(2)

    # print(filename)
    # print(contents)

    # Get putted file and check contents
    try:
        resp = requests.get("http://%s/nfs/%s" % (ip, filename),
                            allow_redirects=False)
        text = resp.text.strip()
    except Exception as E:
        print("Failed to get file via http")
        sys.exit(NOTOK)

    if text != contents:
        print("The file contents is wrong")
        sys.exit(NOTOK)

    print("OK")
    sys.exit(OK)


if __name__ == "__main__":
    print >>sys.stderr, "Using NFS_SERVER_IP: '{0}'".format(NFS_SERVER_IP)
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(TIMEOUT)

    if len(sys.argv) < 2:
        print("Usage: ./nfs.py <ip>")
        sys.exit(CHECKERERROR)

    # cd to script directory
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    ip = sys.argv[1]
    check(ip)
