#!/usr/bin/env python

import pymongo
import json
import sys
import logging
import subprocess
import re
import os

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

def get_shards(db):
    for shard in db.shards.find():
        yield shard["_id"]

def get_shards_count(shard_ids, sh_status):
    shard_chunks_count = {}

    for shard_id in shard_ids:
        m = re.search(r'{0}\s+?(\d+)'.format(shard_id), sh_status, re.MULTILINE)
        if not m:
            print "Can't find shard id in status"
            print >>sys.stderr, "Can't find shard id in status: {0}|{1}".format(shards_id, sh_status)
            sys.exit(STATUS_NOT_OK)
        shard_chunks_count[shard_id] = int(m.group(1))
    return shard_chunks_count

def check_shard_balancing(ip, shard_ids):
    try:
        os.environ['LANG'] = os.environ['LC_ALL'] = 'C'
        sh_status = subprocess.check_output(('mongo', ip, '--eval', 'sh.status()'))
    except subprocess.CalledProcessError as e:
        print "Can't get shards status"
        print >>sys.stderr, "Can't get shards status: {0}".format(e)
        sys.exit(STATUS_NOT_OK)

    if "root.features" not in sh_status:
        print "root.features are not sharded"
        sys.exit(STATUS_NOT_OK)

    shard_count = get_shards_count(shard_ids, sh_status)
    if abs(shard_count.values()[0] - shard_count.values()[1]) > 2:
        print "Shards are not balanced"
        sys.exit(STATUS_NOT_OK)
    print ":)"
    sys.exit(STATUS_OK)

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]

    try:
        client = pymongo.MongoClient(host=(ip))
        db = client.config
        shard_ids = list(get_shards(db))
    except pymongo.errors.PyMongoError as e:
        print "Cant connect to database: {0}".format(e)
        sys.exit(STATUS_NOT_OK)
    if len(shard_ids) != 2:
        print "Shards count should be 2"
        print >>sys.stderr, "Shards count: {0}".format(len(shard_ids))
    check_shard_balancing(ip, shard_ids)
    sys.exit(STATUS_OK)

if __name__ == "__main__":
    main()
