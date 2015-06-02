#!/usr/bin/env python

import pymongo
import json
import sys
import logging
import subprocess
import re
import os
import time
import urllib2

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
from jabber_basic import BasicJabberChecker, CheckerError

JABBER_USER1 = "alice"
JABBER_PASS1 = "Sj7DfjdshsDjhs783Ddjaasd4FV"

JABBER_USER2 = "bob"
JABBER_PASS2 = "D1SjnssCF8y8kSljjhk98uyAasd"

MAX_LINES_TO_READ = 4096

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]

    message = ""
    message_id = ""
    try:
        jabber_checker1 = BasicJabberChecker(ip, "root.yandex.net", JABBER_USER1, JABBER_PASS1)
        jabber_checker1.start()


        jabber_checker2 = BasicJabberChecker(ip, "root.yandex.net", JABBER_USER2, JABBER_PASS2)
        jabber_checker2.start()

        message_id = jabber_checker1._gen_msg_id()
        message = "Hello, Bob!\n\n{0}".format(message_id)
        jabber_checker1.send_message("{0}@root.yandex.net".format(JABBER_USER2), message)
    except CheckerError as e:
        print e.reason
        sys.exit(STATUS_NOT_OK)

    time.sleep(1)

    url = "http://{0}/jabber_archive.txt".format(ip)
    logging.info("Url to check: '%s'", url)

    try:
        url_fn = urllib2.urlopen(url)
        if url_fn.geturl() != url:
            print "Redirects are not allowed!"
            sys.exit(STATUS_NOT_OK)
    except urllib2.URLError as e:
        print "Cant read '{0}' : {1}".format(url, e)
        sys.exit(STATUS_NOT_OK)


    for i, line in enumerate(url_fn):
        if message_id in line:
            print ":)"
            sys.exit(STATUS_OK)

        if i >= MAX_LINES_TO_READ:
            print "jabber_archive.txt is too long"
            sys.exit(STATUS_NOT_OK)

    print "Bad jabber_archive.txt file"
    sys.exit(STATUS_NOT_OK)



if __name__ == "__main__":
    main()
