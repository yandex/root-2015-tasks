#!/usr/bin/env python2
# coding=utf-8
__author__ = 'muzafarov'

import sys
import os

import socket
from collections import Counter
from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
OK = 10
FAIL = 11
ITERATIONS = 100

cipher = PKCS1_v1_5.new(RSA.importKey("""-----BEGIN RSA PRIVATE KEY-----
MIICXwIBAAKBgQC4cqgmcwp9TaeucqhFli0HtmnHKfn5iy91tyoG3o4ZAdU4wIw/
NH5c8IAlPqTo/tYP9O3xUg50ep0/+x3Lp02vjDF851UfnQSoj/z76qtXN66IGXT1
1QpenhGzLIOyex0uh0LuqC96jyQrtIEwsx0BQLGp3jXS0l1BfnHH9U+E7wIDAQAB
AoGBALQxRzaw4smBSNRzLRM2YG2Ndo9c4do5cLcmpscpO1cQ5FZaPWkuBlkTl41L
Qt5gv429MYu1J2wBsYgk8nnXy1qOIj9s73I3rFrEbPPmRRaMcK8MjSVKgDKhuGHG
evRhUljodhpmNT3bWPt5Vt+PXkkkGVaRRM+SxUXyq2aT04AJAkEA9KUnK8STTEtf
sQivzjtCg8gtEJ6ekFGsj4+SIKpMK3/ZhZI3W4HcSetphQyPJnK1du6GnzWD1jO9
V5Oh793FAwJBAMECPyD3Le1/CaLxXoDFStTbp2E3zKj12eKsYvgWBUF8NUSMUqIz
xQNN2dvc5AbLTA//NSH3j4JtJJbh8zZTLqUCQQCMSoDx+mI1qCuRy9d1PkpgY9Rj
6XIodI2uLbiwfrf7Ye+NR1Hzab63rQXvxEn61GD3eMU+W2Pk2/rCU+jTMqudAkEA
rDL77cZ6lIUeLOFaZlsfq4+Z41PsZeaLEgCpgBvtboKJ5/GmHA9CO/NuZwnJ7AHf
h/ozBm4f/MaxuWg4HQTT/QJBALOQQvoiz3oohY3txw/D9xeGE1fu8qZFb1nMFS8B
vvCVVCAcYCF/V+owe2gnJgFoGXARWcNOZy0q7RDrqADl6Y4=
-----END RSA PRIVATE KEY-----
"""))


def decryptRSA(s):
    try:
        s = b64decode(s)
        s = cipher.decrypt(s, None)
        return s
    except:
        return ""

if __name__ == '__main__':
    server = sys.argv[1] if len(sys.argv) > 1 else 'image2'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
    ports = Counter()
    last_time = 0

    for i in xrange(ITERATIONS):
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((server, port))
            data = decryptRSA(sock.recv(1024))
            if data == 0 or data == "":
                ports[0] += 1
                continue

            recv_port = data[:4]
            recv_time = float(data[4:])
            if recv_time >= (last_time - 5):
                ports[recv_port] += 1
                last_time = recv_time
            sock.close()
        except socket.timeout:
            ports[0] += 1
        except socket.error:
            print "Can't connect to %s:%s" % (server, port)
            sys.exit(FAIL)
        except Exception as e:
            print "Something wrong with you: %s" % e
            sys.exit(FAIL)

    sys.stderr.write("{0}:{1}\t{2}\n".format(server, port, ports))
    if ports[0] > 490:
        print "Can't parse response in %s times" % ports[0]
        sys.exit(FAIL)
    del ports[0]
    avg = sum(ports.values()) / len(ports)
    for p, c in ports.items():
        if avg - 5 > c:
            print "Daemon {0} is too rare".format(p[-1] if len(p) > 2 else 0)
            sys.exit(FAIL)
        if c > avg + 5:
            print "Daemon {0} is too often".format(p[-1] if len(p) > 2 else 0)
            sys.exit(FAIL)

    sys.exit(OK)
