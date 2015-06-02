#!/usr/bin/env python

import hashlib
import enet
import sys
import socket


STATUS_OK = 10
STATUS_NOT_OK = 11


def done(status, message=None, log=None):
    if message:
        print message
    if log:
        print >> sys.stderr, log
    sys.exit(status)


def send_hint(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'enet error', (ip, 13000))


def main():
    host = enet.Host(None, 1, 0, 0)
    peer = host.connect(enet.Address(sys.argv[1], 13000), 1)

    data = hashlib.md5(sys.argv[1] + 'R0Ot14').hexdigest()
    tries = 0

    while True:
        evt = host.service(100)
        if evt.type == enet.EVENT_TYPE_NONE:
            tries += 1
            if tries > 10:
                send_hint(sys.argv[1])
                done(STATUS_NOT_OK, "Timeout", "Timeout")
        elif evt.type == enet.EVENT_TYPE_CONNECT:
            peer.send(0, enet.Packet(data))
        elif evt.type == enet.EVENT_TYPE_RECEIVE:
            r_data = evt.packet.data
            peer.disconnect()

            if r_data == data:
                done(STATUS_OK)

            fail("received '%s' but '%s' expected" % (r_data, data))
        else:
            fail("invalid event type: '%s'" % evt.type)


if __name__ == '__main__':
    main()
