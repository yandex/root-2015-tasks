#!/usr/bin/env python

import os
import sys
import json
import random
import logging

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ETALON_FILENAME = os.path.join(CUR_DIR, "etalon.jsons")
ITERATIONS = 100

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

sys.path.append(CUR_DIR)

from svn import Svn

def check(ip):
    svn_url = "svn://{0}".format(ip)

    etalon = []
    with open(ETALON_FILENAME) as fn:
        for line in fn:
            etalon.append(json.loads(line))

    svn = Svn(svn_url)
    rev = svn.info()["rev"]

    if rev != len(etalon) - 1:
        print "Wrong revisions number"
        sys.exit(STATUS_NOT_OK)

    for _ in xrange(ITERATIONS):
        et = random.choice(etalon)
        rev = et["rev"]
        files = et["files"]

        for r_file in svn.ls(rev=rev):
            #logging.info("Checking rev: %d, file '%s', size %d", rev, r_file["name"], r_file["size"])
            if r_file["name"] not in files:
                print "File '{0}' in rev {1} should be deleted".format(r_file["name"], rev)
                sys.exit(STATUS_NOT_OK)

            e_file = files[r_file["name"]]
            if e_file["deleted"]:
                print "File '{0}' should be deleted in rev {1}".format(e_file["name"], rev)
                sys.exit(STATUS_NOT_OK)

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    try:
        check(ip)

    except AttributeError:
        print "Looks like no repo :("
        sys.exit(STATUS_NOT_OK)

    except Exception as e:
        print e
        sys.exit(STATUS_NOT_OK)


    sys.exit(STATUS_OK)

if __name__ == "__main__":
    main()
