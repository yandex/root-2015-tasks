#!/usr/bin/env python

import enet
import sys


def main():
    host = enet.Host(enet.Address(b'0.0.0.0', 13000), 100, 0, 0)

    while True:
        evt = host.service(0)
        if evt.type == enet.EVENT_TYPE_RECEIVE:
            data = evt.packet.data
            print "%s -> '%r'" % (evt.peer.address, data)
            if evt.peer.send(0, enet.Packet(data)) < 0:
                print >> sys.stderr, "send error"

if __name__ == '__main__':
    main()
