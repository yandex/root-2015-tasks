#!/usr/bin/env python
# coding: utf-8

import sys
import urllib2
import urllib
import dns.resolver
import random
import string
import socket
import re
import threading
import time

import xmpp

class CheckerError(Exception):
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason

class BasicJabberChecker(object):
    def __init__(self, ip, hostname, username, password, timeout=10):
        self.ip = ip
        self.hostname = hostname
        self.username = username
        self.password = password
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.nameservers = [ip]
        self.dns_resolver.lifetime = timeout

        self.connect()
        self.auth()

        self.register_handler('message', self.message_handler)

        self.thread = None
        self.messages = []

    @staticmethod
    def _gen_msg_id():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))

    def _get_ip_by_name(self, hostname, _type='A'):
        if self.ip == "192.168.26.12":
            if _type == "A":
                return (True, "192.168.26.12")

            if _type == "SRV":
                return (True, ("192.168.26.12", 5222))


        try:
            answers = self.dns_resolver.query(hostname, _type)
            rdata = answers[0]

            if _type == "A":
                return (True, rdata.address)

            if _type == "SRV":
                port = rdata.port

                status, result = self._get_ip_by_name(rdata.target, 'A')
                if not status:
                    return (status, result)

                ip = result
                if ip != self.ip:
                    raise CheckerError(False, "Jabber server should be on '{0}'".format(self.ip))

                return (True, (ip, port))

        except dns.resolver.NoAnswer as e:
            raise CheckerError(False, "Bad answer from DNS-server")

        except dns.resolver.Timeout as e:
            raise CheckerError(False, "No answer from DNS-server")

        except CheckerError:
            raise

        except Exception as e:
            raise CheckerError(None, "Unknown exception while resolving")

    def connect(self):
        status, result = self._get_ip_by_name("_jabber._tcp." + self.hostname, "SRV")
        if not status:
            status, result = self._get_ip_by_name("_xmpp-server._tcp." + self.hostname, "SRV")

            if not status:
                return status, result

        jabber_server_ip, port = result

        self.conn = xmpp.Client(self.hostname)
        conn_result = self.conn.connect((jabber_server_ip, 5222), use_srv=False)

        if not conn_result:
            raise CheckerError(False, "Can't connect to jabber server: {0}".format(jabber_server_ip, port))

        return (True, "Connected")

    def auth(self):
        auth_result = self.conn.auth(self.username, self.password)
        if not auth_result:
            raise CheckerError(False, "Bad username or password")

        return (True, "OK")

    def register_handler(self, name, handler):
        self.conn.RegisterHandler(name, handler)

    def step_on(self):
        try:
            self.conn.Process(1)
        except KeyboardInterrupt:
            return 0

        return 1

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.setDaemon(True)
        self.thread.start()

    def _run(self):
        self.conn.sendInitPresence()
        while self.step_on(): pass


    def send_message(self, uid, msg_body):
        self.conn.send(xmpp.Message(uid, msg_body))

    def message_handler(self, conn, mess): #вызывается при входящем сообщении,
        # text = mess.getBody() #получаем текст сообщения, отправителя
        # user = mess.getFrom() #и шлём обратно
        # reply = text
        #conn.send(xmpp.Message(mess.getFrom(), reply))
        self.messages.append(mess)


if __name__ == "__main__":
    jabber_checker1 = BasicJabberChecker("192.168.26.12", "root.yandex.net", "test", "qwer")
    jabber_checker1.start()
    jabber_checker1.send_message("test1@root.yandex.net", "Hello! Test!")

    jabber_checker2 = BasicJabberChecker("192.168.26.12", "root.yandex.net", "test1", "qwer")
    jabber_checker2.start()

    time.sleep(2)
    print jabber_checker2.messages
    msg = jabber_checker2.messages.pop(0)
    print msg.getBody()
