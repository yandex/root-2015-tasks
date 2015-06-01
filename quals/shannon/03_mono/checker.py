#!/usr/bin/env python3

import math
import socket
import sys


STATUS_OK = 10
STATUS_NOT_OK = 11


def done(status, message=None, log=None):
    if message:
        print(message)
    if log:
        print(log, file=sys.stderr)
    sys.exit(status)


def check(command, ip, checker):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, 12354))
    except Exception as e:
        done(STATUS_NOT_OK, "No connection", str(e))

    sock.sendall((command + '\n').encode('utf-8'))
    answer = b''
    while True:
        ans = sock.recv(1024)
        if not ans:
            break
        answer += ans
    checker(answer.decode('utf-8'))
    sock.close()


def make_size_checker(expected, message):
    def _check(ans):
        try:
            if int(ans) == expected:
                return
        except ValueError:
            pass

        done(STATUS_NOT_OK, message,
             "{}: '{}' expected but '{}' given".format(
                 message, expected, ans))

    return _check


def make_text_checker(expected, message):
    def _check(ans):
        for item in expected:
            if item not in ans:
                done(STATUS_NOT_OK, message,
                     "{}: '{}' expected in '{}'".format(message, item, ans))

    return _check


def make_string_checker(expected, message):
    return make_text_checker((expected,), message)


def make_float_checker(expected, message):
    def _check(ans):
        if math.fabs(float(ans) - expected) >= 1e-6:
            done(STATUS_NOT_OK, message,
                 "{}: '{}' expected but '{}' given".format(
                     message, expected, ans))

    return _check


def main():
    ip = sys.argv[1]
    check('sz 1.exe', ip, make_size_checker(32768, "invalid '1.exe' size"))
    for fname in ('/dev/zero', '/proc/cpuinfo', '/dev/random',
                  '/proc/uptime', '/proc/version'):
        check('sz {}'.format(fname), ip,
              make_size_checker(0, "invalid '{}' size".format(fname)))

    check('cat /proc/cpuinfo', ip,
          make_text_checker(('processor', 'vendor_id', 'cpu cores', 'MHz'),
                            'invalid cpuinfo'))
    check('cat /proc/version', ip,
          make_text_checker(('Linux version', 'ARCH', 'gcc version'),
                            'invalid OS version'))

    check('info Е00', ip, make_string_checker('Explosiv music', 'bad program'))

    check('clx 5', ip, make_string_checker('3101 + 0i', 'bad program'))
    check('clx 0', ip, make_string_checker('NaN', 'bad program'))

    check('erf 0.1', ip, make_float_checker(0.112462916018285, 'bad program'))
    check('erf 0.5', ip, make_float_checker(0.520499877813047, 'bad program'))
    check('erf 1', ip, make_float_checker(0.842700792949715, 'bad program'))
    check('erf 10', ip, make_float_checker(1.0, 'bad program'))

    done(STATUS_OK)


if __name__ == '__main__':
    main()
