#!/usr/bin/env python3

import os
import sys
import mysql as mariadb


USER = 'checker'
PASS = 'masterkey'

STATUS_OK = 10
STATUS_NOT_OK = 11

CHECK = 960329


def done(status, message=None, log=None):
    if message:
        print(message)
    if log:
        print(log, file=sys.stderr)
    sys.exit(status)


def check(connection):
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT * FROM db.data LIMIT 10')
        checksum = sum(map(lambda x: x[2], cursor))
        if checksum != CHECK:
            done(STATUS_NOT_OK,
                 "Invalid database or was modified",
                 "Checksum is '{}' but '{}' expected".format(checksum, CHECK))
    except mariadb.Error as e:
        done(STATUS_NOT_OK, str(e), e)
    finally:
        cursor.close()


def main():
    ip = sys.argv[1]
    try:
        db = mariadb.connect(host=ip, user=USER, password=PASS)
    except mariadb.Error as e:
        done(STATUS_NOT_OK, str(e), e)

    try:
        check(db)
    finally:
        db.close()

    done(STATUS_OK)


if __name__ == '__main__':
    main()
