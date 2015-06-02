#!/usr/bin/env python

import json
import sys
import logging
import subprocess
import re
import os
import time
import signal

STATUS_OK = 10
STATUS_NOT_OK = 11
STATUS_INTERNAL_ERROR = 100

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
from jabber_basic import BasicJabberChecker, CheckerError

JABBER_USER1 = "alice"
JABBER_PASS1 = "Sj7DfjdshsDjhs783Ddjaasd4FV"

JABBER_USER2 = "bob"
JABBER_PASS2 = "D1SjnssCF8y8kSljjhk98uyAasd"

def main():
    logging.basicConfig(format="%(asctime)-15s:%(levelname)s:%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} ip".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]

    try:
        jabber_checker1 = BasicJabberChecker(ip, "root.yandex.net", JABBER_USER1, JABBER_PASS1)
        jabber_checker1.start()


        jabber_checker2 = BasicJabberChecker(ip, "root.yandex.net", JABBER_USER2, JABBER_PASS2)
        jabber_checker2.start()

        message = "Hello, Bob!\n\n{0}".format(jabber_checker1._gen_msg_id())
        jabber_checker1.send_message("{0}@root.yandex.net".format(JABBER_USER2), message)
    except CheckerError as e:
        print e.reason
        sys.exit(STATUS_NOT_OK)

    time.sleep(1)
    for msg in jabber_checker2.messages:
        if msg.getBody() == message:
            sys.exit(STATUS_OK)

    print >>sys.stderr, "Did no recv message in 1 second!"
    sys.exit(STATUS_NOT_OK)



if __name__ == "__main__":
    main()
