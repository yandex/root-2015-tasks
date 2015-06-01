#!/usr/bin/env python

import os
import sys
import json
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from svn import Svn

MAX_FILE_SIZE = 5 * 1024 * 1024

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    svn_url = sys.argv[1]

    svn = Svn(svn_url)
    max_rev = svn.info()["rev"]

    deleted_files = set()
    for rev in xrange(max_rev + 1):
        info = {}
        info["rev"] = rev
        files = {}
        for f in svn.ls(rev=rev):
            f["deleted"] = False
            if f["name"] in deleted_files or f["size"] > MAX_FILE_SIZE:
                deleted_files.add(f["name"])
                f["deleted"] = True
            files[f["name"]] = f
        info["files"] = files
        print json.dumps(info)




if __name__ == "__main__":
    main()
