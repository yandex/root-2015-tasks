#!/usr/bin/env python2

from twisted.web import proxy, http
from twisted.internet import reactor, protocol

from twisted.web.proxy import Proxy, ProxyRequest, ProxyClient, ProxyClientFactory
from twisted.web.http import parse_qs, HTTPFactory
from twisted.python import log

import multiprocessing
import time
import sys

class ProxyFilterClientFactory(ProxyClientFactory):
    protocol = ProxyClient
    def buildProtocol(self, address):
        if self.father.allowed_address != address.host:
            log.msg("Host {0} is not allowed!".format(address.host), system="address_filter")
            self.father.setResponseCode(403, "Host not allowed!")
            self.father.finish()
            return protocol.Protocol()

        log.msg("Host {0} is allowed!".format(address.host), system="address_filter")
        return ProxyClientFactory.buildProtocol(self, address)


class ProxyFilterRequest(ProxyRequest):
    protocols = {'http': ProxyFilterClientFactory}

    def __init__(self, allowed_address, *args, **kwargs):
        self.allowed_address = allowed_address
        ProxyRequest.__init__(self, *args, **kwargs)

class ProxyFilterRequestFactory(object):
    def __init__(self, allowed_address):
        self.allowed_address = allowed_address

    def __call__(self, *args, **kwargs):
        return ProxyFilterRequest(self.allowed_address, *args, **kwargs)


class ProxyFilter(Proxy):
    #requestFactory = ProxyFilterRequest

    @property
    def requestFactory(self):
        return ProxyFilterRequestFactory(self.allowed_address)

    def __init__(self, allowed_address, *args, **kwargs):
        self.allowed_address = allowed_address
        Proxy.__init__(self, *args, **kwargs)

class ProxyFilterFactory(HTTPFactory):
    def __init__(self, allowed_address, *args, **kwargs):
        self.allowed_address = allowed_address
        HTTPFactory.__init__(self, *args, **kwargs)

    def buildProtocol(self, address):
        return ProxyFilter(self.allowed_address)

def start_proxy(reactor):
    log.startLogging(sys.stderr)
    reactor.run()

def start_proxy_proc(allowed_address):
    port = reactor.listenTCP(0, ProxyFilterFactory(allowed_address)).getHost().port
    p = multiprocessing.Process(target=start_proxy, args=(reactor,))
    p.daemon = True
    p.start()
    return (port, p)

def main():
    print start_proxy_proc('194.226.244.126')
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
