#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
import pymysql as mariadb
import time


USER = 'checker'
PASS = 'masterkey'

STATUS_OK = 10
STATUS_NOT_OK = 11


def done(status, message=None, log=None):
    if message:
        print(message)
    if log:
        print(log, file=sys.stderr)
    sys.exit(status)


def test_query(cursor, query, answer, threshold):
    t_start = time.time()
    cursor.execute(query)
    checksum = sum(map(lambda x: x[0], cursor))
    if checksum != answer:
        done(STATUS_NOT_OK,
             "Invalid database or was modified",
             "Checksum of '{}' was '{}' but '{}' expected".format(
                 query, checksum, answer))
    t_end = time.time()

    if t_end - t_start > threshold:
        done(STATUS_NOT_OK, "Too long time",
             "Time of '{}' was '{}'".format(query, t_end - t_start))


def check(connection):
    cursor = connection.cursor()
    try:
        test_query(cursor, 'SELECT COUNT(*) FROM db.data WHERE size < 10',
                   444724, 3.0)
        test_query(cursor, 'SELECT MAX(hits) FROM db.data',
                   12252257, 3.0)
        test_query(cursor,
                   'SELECT hits FROM db.data ORDER BY hits DESC LIMIT 10',
                   64165894, 3.0)
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
