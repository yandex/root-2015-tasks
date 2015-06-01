#!/usr/bin/env python3

import socket
import sys
import signal
import random

# CONSTS
OK = 10
NOTOK = 11
CHECKERERROR = 100

TIMEOUT = 20
PORT = 3255

DATALEN = 32


def getrightans(data):
    state = 55
    state2 = 70

    ans = b""

    for d in data:
        if d % 2 == 0:
            state += d
        else:
            state -= d

        state %= 256

        if state % 2 == 0:
            state2 -= state
        else:
            state2 += state

        state2 %= 256

        ans += bytes([state2])
    return ans


def check(ip):
    try:
        s = socket.create_connection((ip, PORT))
    except Exception:
        print("Can't connect")
        sys.exit(NOTOK)

    s.recv(4)  # recv hi! string. Hope it is fits in tcp window

    data = bytes([random.randrange(256) for _ in range(DATALEN)])

    s.sendall(data)

    ans = b""

    for i in range(DATALEN):
        ans += s.recv(1)
    # print(ans)

    right_ans = getrightans(data)
    # print(right_ans)

    if ans == right_ans:
        print("Ok")
        sys.exit(OK)
    else:
        print("Not ok")
        sys.exit(NOTOK)


if __name__ == "__main__":
    signal.alarm(TIMEOUT)

    if len(sys.argv) < 2:
        print("Usage: ./07_exec.py <ip>")
        sys.exit(CHECKERERROR)

    ip = sys.argv[1]
    check(ip)
