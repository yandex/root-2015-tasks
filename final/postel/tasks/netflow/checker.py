#!/usr/bin/env python2

import os.path
from random import randint
import re
import socket
import sys
import time
import urllib2
from dpkt.netflow import Netflow5


STATUS_OK = 10
STATUS_NOT_OK = 11

def ip2int(ip):
    result = 0
    for (i, v) in enumerate(ip.split('.')):
        result += int(v) * (256 ** (3 - i))
    return result

SUBNET_IP = ip2int('220.123.31.0')
EXCLUDE_MASK = 19

def send_flow_packet(sock, ip, port, baseip):
    with open('/proc/uptime') as f:
        uptime = int(f.read().split()[0].split('.')[0])
    epoch = int(str(time.time()).split('.')[0])

    n = randint(1, 30)
    packets = ''
    for i in xrange(n):
        sip = 0
        if randint(0, 3) == 2:
            sip = baseip
        else:
            while sip % EXCLUDE_MASK == 0:
                sip = randint(0, 255)
        sip += SUBNET_IP

        dip = randint(0, 255 ** 4)
        pcount = randint(1, 50)
        bcount = randint(1, 300000)
        stime = uptime - randint(1, 300)
        etime = stime + randint(1, 300)
        sport = randint(0, 20000)
        dport = randint(0, 20000)
        proto = randint(0, 17)
        if randint(0, 2):
            saddr, daddr = sip, dip
        else:
            saddr, daddr = dip, sip

        packets += Netflow5.NetflowRecord(src_addr=saddr, dst_addr=daddr,
                                          pkts_sent=pcount, bytes_sent=bcount,
                                          start_time=stime, end_time=etime,
                                          src_port=sport, dst_port=dport,
                                          ip_proto=proto).pack()

    sock.sendto(Netflow5(version=5, sys_uptime=uptime, unix_sec=epoch,
                         data=packets).pack(), (ip, port))


def generate_flow(n=1000, ip='127.0.0.1', port=9996):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    base = 1
    for i in xrange(n):
        send_flow_packet(sock, ip, port, base)
        base += 1
        if base % EXCLUDE_MASK == 0:
            base += 1
        if base > 254:
            base = 1


def done(status, message=None, log=None):
    if message:
        print message
    if log:
        print >>sys.stderr, log
    sys.exit(status)


def check(ip):
    try:
        _url = 'http://%s/billing.html' % ip
        f = urllib2.urlopen(_url)
        if f.geturl() != _url:
            done(STATUS_NOT_OK, "Redirects are not allowed!", "redirects :(")

        page = f.read()

        _rows = re.findall(r'<tr>(.*?)</tr>', page, re.IGNORECASE | re.DOTALL)
        if len(_rows) < 2:
            done(STATUS_NOT_OK, "No data. Try again after 1 minute", "No data")

        rows = []
        for row in _rows:
            row = re.findall(r'<td>\s*(.*?)\s*</td>',
                             row.strip(), re.IGNORECASE)
            if len(row) == 2:
                rows.append(row)

        ips = set()
        for (i, row) in enumerate(rows):
            if i > 0 and int(rows[i - 1][1]) < int(row[1]):
                done(STATUS_NOT_OK, "wrong order", "wrong order")

            try:
                ips.add(int(row[0].split('.')[-1]))
            except Exception as e:
                done(STATUS_NOT_OK, "wrong format", str(e))

        for i in xrange(1, 255):
            if ((i % EXCLUDE_MASK and i not in ips) or
                (i % EXCLUDE_MASK == 0 and i in ips)):
                done(STATUS_NOT_OK, "wrong answer", "wrong answer")
    except (urllib2.URLError, urllib2.HTTPError) as e:
        done(STATUS_NOT_OK, "urlopen failed", str(e))

def main():
    ip = sys.argv[1]
    generate_flow(ip=ip)
    check(ip)
    done(STATUS_OK)


if __name__ == '__main__':
    main()
