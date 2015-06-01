#!/usr/bin/env python

import os
import sys
import json
import random
import logging
import re

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ETALON_FILENAME = os.path.join(CUR_DIR, "etalon.jsons")
ITERATIONS = 100

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

RE_REVISION = re.compile(r'Revision-number: (\d+)')
RE_NODE_PATH = re.compile(r'Node-path: (.*)')
RE_NODE_ACTION = re.compile(r'Node-action: (.*)')

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)

    etalon = []
    deleted_files = set()
    files_in_repo = set()
    name = ""
    out = True
    with open(ETALON_FILENAME) as fn:
        for line in fn:
            etalon.append(json.loads(line))

    for line in sys.stdin:
        m = RE_REVISION.match(line)
        if m:
            rev = int(m.group(1))
            logging.info("Revision-number %d", rev)
            out = True

        m = RE_NODE_PATH.match(line)
        if m:
            name = m.group(1)
            if name in deleted_files:
                out = False
                continue
            logging.info("Name %s", name)
            et_file = etalon[rev]["files"].get(name)
            out = True
            if et_file and et_file["deleted"]:
                deleted_files.add(et_file["name"])
                out = False
                if name in files_in_repo:
                    sys.stdout.write("Node-path: {0}\n".format(name))
                    sys.stdout.write("Node-action: delete\n\n")
                files_in_repo.discard(name)

        m = RE_NODE_ACTION.match(line)
        if m:
            action = m.group(1)
            if action == "add":
                files_in_repo.add(name)

        if out:
            sys.stdout.write(line)




if __name__ == "__main__":
    main()
