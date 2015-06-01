#!/usr/bin/env python

import os
import sys
import subprocess

STATUS_OK = 10
STATUS_NOT_OK = 11

RET_CODE_OK = 0
RET_CODE_BAD_CERT = 60
RET_CODE_BAD_PROTO = 35

class OpenSSL_SClient_Parsert(object):
    def __init__(self, openssl_out):
        self.openssl_out = openssl_out

def done(status, message=None, log=None):
    if message:
        print(message)
    if log:
        print >>sys.stderr, log
    sys.exit(status)


def check_curl(ip, proto=""):
    if proto:
        proto = "--" + proto
    try:
        out = subprocess.check_output(["curl", proto, "-s", "https://{0}/".format(ip)])
    except subprocess.CalledProcessError as e:
        if e.returncode in (RET_CODE_BAD_CERT, RET_CODE_BAD_PROTO):
            return e.returncode
        done(STATUS_NOT_OK, "Curl error")
    return RET_CODE_OK

def check_openssl(ip):
    proc = subprocess.Popen(["openssl", "s_client", "-connect", "{0}:443".format(ip)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write("GET / HTTP/1.0\r\n\r\n")
    stdout = proc.stdout.read()
    print stdout

def main():
    ip = sys.argv[1]
    ret = check_curl(ip)
    if ret == RET_CODE_BAD_CERT:
        done(STATUS_NOT_OK, "Certificate verification failed")

    ### TODO
    #if check_curl(ip, "sslv2") != RET_CODE_BAD_PROTO:
    #    done(STATUS_NOT_OK, "SSLv2 is weak")

    if check_curl(ip, "sslv3") != RET_CODE_BAD_PROTO:
        done(STATUS_NOT_OK, "SSLv3 is weak")

    ### TODO
    #check_openssl(ip)
    done(STATUS_OK, "OK")


if __name__ == '__main__':
    main()
