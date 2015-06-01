#!/usr/bin/env python

import json
import sys
import logging
import subprocess
import re
import os
import tempfile
import shutil
import time
from mercurial import ui, hg

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../common'))

import proxy

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

def check_bigfiles(repo):
    for c in repo.changelog:
        got_osm = False
        for filename in repo[c]:
            if filename.endswith(".gz"):
                print "Got gz file in {0}".format(repo[c])
                sys.exit(STATUS_NOT_OK)
            if filename == "2.osm":
                got_osm = True
        if not got_osm:
            print "Cant find osm file in {0}".format(repo[c])
            sys.exit(STATUS_NOT_OK)

def main():
    os.environ['LANG'] = os.environ['LC_ALL'] = 'C'
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]

    proxy_port, proxy_proc = proxy.start_proxy_proc(ip)

    tmp_dir = tempfile.mkdtemp()
    url = "http://{0}:8000/".format(ip)

    try:
        sh_status = subprocess.check_call(('nice', 'hg', "--config", "http_proxy.host=127.0.0.1:{0}".format(proxy_port), 'clone', url, tmp_dir))
        repo = hg.repository(ui.ui(), tmp_dir)
        check_bigfiles(repo)
    except subprocess.CalledProcessError as e:
        print "Cant clone repo".format(e)
        sys.exit(STATUS_NOT_OK)
    finally:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
    sys.exit(STATUS_OK)

if __name__ == "__main__":
    main()
