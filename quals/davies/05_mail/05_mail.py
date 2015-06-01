#!/usr/bin/env python2
# coding=utf-8
import uuid
import subprocess

__author__ = 'muzafarov'

import sys
import os
from smtplib import SMTP_SSL, SMTP
from email.mime.text import MIMEText
import imaplib
OK = 10
FAIL = 11
AMU_KEYFILE = "amu_key"

subject = "Important Root Message"
content = "Test message from {0}"


SSH_ARGS = ["ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "CheckHostIP=no",
            "-o", "NoHostAuthenticationForLocalhost=yes",
            "-o", "BatchMode=yes",
            "-o", "LogLevel=ERROR",
            "-o", "UserKnownHostsFile=/dev/null",
            "-t", "-t",
            "-l", "amu"]

def send_mail(server, user, receiver):
    result = FAIL
    try:
        msg = MIMEText(content.format(user[0]), 'plain')
        msg['Subject'] = subject
        msg['From'] = user[0] + '@root'

        conn = SMTP_SSL(server)
        conn.set_debuglevel(False)
        conn.login(user[0], user[1])
        try:
            conn.sendmail(user[0] + '@root', receiver[0] + '@root', msg.as_string())
            result = OK
        except Exception as e:
            print "Cant send message: {0}".format(e)
            result = FAIL
        finally:
            conn.close()
            return result
    except Exception as e:
        print "Cant send message: {0}".format(e)
        return FAIL

def get_imap(server, sender, user):
    result = FAIL
    try:
        box = imaplib.IMAP4_SSL(server)
        box.login(*user)
        box.select()
        typ, data = box.search(None, 'FROM', '"{0}"'.format(sender[0]))
        for num in data[0].split():
            typ, data = box.fetch(num, '(RFC822)')
            if content.format(sender[0]) in data[0][1]:
                result = OK
            box.store(num, '+FLAGS', '\\Deleted')

        box.expunge()
        box.close()
        box.logout()
        return result
    except Exception as e:
        print "IMAP error: {0}".format(e)
        return FAIL

def check_call_remote(server, cmd):
    os.chmod(AMU_KEYFILE, 0400)
    subprocess.check_call(SSH_ARGS + ['-i', AMU_KEYFILE, server, cmd])

def create_user(server):
    username = uuid.uuid4().get_hex()[:10]
    password = uuid.uuid4().get_hex()

    try:
        check_call_remote(server, 'sudo -n amu "{0}" "{1}"'.format(username, password))
    except Exception as e:
        print "Error while creating user: {0}".format(e)
        sys.exit(FAIL)

    return (username, password)

if __name__ == '__main__':
    server = sys.argv[1] if len(sys.argv) > 1 else 'image2'

    # cd to script directory
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    try:
        check_call_remote(server, 'sudo -n iptables -I INPUT -p tcp -m multiport --dports 25,587 -j REJECT >/dev/null 2>/dev/null')
    except Exception as e:
        print >>sys.stderr, "Err while running iptables"
    else:
        print "Oops"
        sys.exit(FAIL)

    user1, user2 = create_user(server), create_user(server)
    if send_mail(server, user1, user2) == OK:
        print "Send OK"
        sys.exit(get_imap(server, user1, user2))
    sys.exit(FAIL)
