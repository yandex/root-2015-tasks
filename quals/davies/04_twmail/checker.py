#!/usr/bin/env python2
# coding=utf-8
import uuid

__author__ = 'muzafarov'

import sys
import os
import subprocess
from smtplib import SMTP
from email.mime.text import MIMEText
import poplib
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
        msg['From'] = "@" + user[0]

        conn = SMTP(server)
        conn.set_debuglevel(False)
        conn.login(user[0], user[1])
        try:
            conn.sendmail("@" + user[0], "@" + receiver[0], msg.as_string())
            result = OK
        except:
            result = FAIL
        finally:
            conn.close()
            return result
    except Exception as e:
        print "Error while sending mail"
        print e
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


def get_pop3(server, user, sender):
    result = FAIL
    try:
        box = poplib.POP3(server)
        box.user(user[0])
        box.pass_(user[1])
        response, lst, octets = box.list()
        for msgnum, msgsize in [i.split() for i in lst]:
            resp, lines, octets = box.retr(msgnum)
            msgtext = " ".join(lines)
            if content.format(sender[0]) in msgtext:
                result = OK
            box.dele(msgnum)

        box.quit()
        return result
    except Exception as e:
        print "Error while recivieng mail"
        print e
        return FAIL

if __name__ == '__main__':
    # cd to script directory
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    server = sys.argv[1] if len(sys.argv) > 1 else 'image2'
    user1, user2 = create_user(server), create_user(server)
    if send_mail(server, user1, user2) == OK:
        sys.exit(get_pop3(server, user2, user1))
    sys.exit(FAIL)
