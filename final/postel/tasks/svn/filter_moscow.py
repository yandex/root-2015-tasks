#!/usr/bin/env python

import sys
import re

#<node id="1550612880" lat="37.1700923" lon="-4.1161304" timestamp="2011-12-17T17:24:11Z" version="1" changeset="10140082" user="Juan Pedro Ruiz" uid="277648"/>
TAG_NODE = re.compile(r'\<node.*?lat="(.*?)".*?lon="(.*?)".*changeset="(\d+)".*(.)>')

#[[[37.290502,55.4913076],[37.290502,55.9576988],[37.9674277,55.9576988],[37.9674277,55.4913076],[37.290502,55.4913076]]]

def main():
    print_all = False
    for line in sys.stdin:
        if print_all:
            line = line.strip()
            sys.stdout.write(line)
            if "</node>" in line:
                sys.stdout.write("\n")
                print_all = False
            #print >>sys.stderr, str(print_all)
            continue

        m = TAG_NODE.search(line)
        if not m:
            continue
        lat = float(m.group(1))
        lon = float(m.group(2))
        changeset = int(m.group(3))
        #print_all = (m.group(4) != "/")

        #print >>sys.stderr, "LAT: {0} LON: {1} {2}".format(lat, lon, print_all)
        #LAT: 48.5191234 LON: 14.5066085
        if (55.4913076 <= lat <= 55.9576988) and (37.290502 <= lon <= 37.9674277):
            print_all = (m.group(4) != "/")
            if print_all:
                line = line.strip()
            sys.stdout.write(line)
            #print >>sys.stderr, "LAT: {0} LON: {1} {2}".format(lat, lon, print_all)
            #print >>sys.stderr, "OUT {0}".format(print_all)


if __name__ == "__main__":
    main()
