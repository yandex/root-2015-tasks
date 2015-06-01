#!/usr/bin/env python

import sys
import re
import os
import sys
import itertools
import subprocess

def main():
    osm = []
    with open(sys.argv[1]) as osm_fn:
        osm = osm_fn.readlines()
    for i, p in enumerate(itertools.permutations(osm, len(osm)/10)):
        print "==== {0} ======".format(i)
        with open("repo/2.osm", "w") as w:
            for k in p:
                w.write(k)
        subprocess.check_call(["gzip", "-f", "-k", "--best", "2.osm"], cwd="repo")
        subprocess.check_call(["hg", "commit", "-A", "-m", "Fix :)", "repo"])
        #sys.exit(0)

if __name__ == "__main__":
    main()
