#!/usr/bin/env python2

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sctp'))

import socket
import sctp
import signal

# CONSTS
OK = 10
NOTOK = 11
CHECKERERROR = 100

TIMEOUT = 18
PORT = 2000
RECV_BUF_SIZE = 65535

def alarm_handler(signum, frame):
    print("No answer")
    sys.exit(NOTOK)

def check(ip):
    sk = sctp.sctpsocket_tcp(socket.AF_INET)
    try:
        sk.connect((ip, PORT))
    except Exception:
        print("Can't connect")
        sys.exit(NOTOK)

    # hope the strings are too small to fit in recv window
    data_to_send = ["Hello", "you've", "solved", "this", "task"]

    for data in data_to_send:
        sk.sctp_send(data + "\n")
        host, flags, msg, notif = sk.sctp_recv(RECV_BUF_SIZE)

        if msg != data + "\n":
            print("Wrong answer")
            sys.exit(NOTOK)

    sk.close()
    print("All ok")
    sys.exit(OK)


if __name__ == "__main__":
    signal.alarm(TIMEOUT)
    signal.signal(signal.SIGALRM, alarm_handler)

    if len(sys.argv) < 2:
        print("Usage: ./01_sctp.py <ip>")
        sys.exit(CHECKERERROR)

    # cd to script directory
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    ip = sys.argv[1]
    check(ip)
