#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
import pymysql as mariadb
from urllib.parse import unquote

HOST = '192.168.26.3'
USER = 'checker'
PASS = 'wrongpass'


def preparedb(connection):
    cursor = connection.cursor()
    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS db')
        cursor.execute('CREATE OR REPLACE TABLE db.data '
                       '(name TEXT CHARSET UTF8, hits INTEGER, size INTEGER)')
        connection.commit()
    finally:
        cursor.close()


def insertdata(connection, filename):
    cursor = connection.cursor()
    try:
        with open(filename, errors='replace') as f:
            for (idx, line) in enumerate(f):
                s = line.strip().split(' ')
                cursor.execute('INSERT INTO db.data VALUES (%s, %s, %s)',
                               (unquote(s[1]), s[2], s[3]))

                if not idx%50000:
                    connection.commit()

        connection.commit()
    finally:
        cursor.close()


def main():
    try:
        connection = mariadb.connect(host=HOST, user=USER, password=PASS)
    except Exception as e:
        sys.exit(str(e))

    try:
        preparedb(connection)
        for name in sys.argv[1:]:
            insertdata(connection, name)
    finally:
        connection.close()


if __name__ == '__main__':
    main()
