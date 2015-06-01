#!/usr/bin/env python

import urllib2
import sys
import logging

GOOD_ROOT_STR = "D2Dfbb4Sxxkl23Dfcs1082"
MAX_LINES_TO_READ = 10

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    url = "http://{0}/root.txt".format(ip)
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
        if GOOD_ROOT_STR in line:
            print ":)"
            sys.exit(STATUS_OK)

        if i >= MAX_LINES_TO_READ:
            print "root.txt is too long"
            sys.exit(STATUS_NOT_OK)

    print "Bad root.txt file (try to find another one)"
    sys.exit(STATUS_NOT_OK)


if __name__ == "__main__":
    main()
