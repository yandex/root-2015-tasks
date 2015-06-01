#!/usr/bin/env python

import sys
import os
import sys
import subprocess
from xml.dom.minidom import parse, getDOMImplementation
from xml.parsers.expat import ExpatError

FNULL = open(os.devnull, 'w')

class Svn(object):
    def __init__(self, repo_url, path=""):
        self.url = repo_url + "/" + path

    @staticmethod
    def _get_xml(cmd):
        xml_el = None
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=FNULL)
        try:
            xml_el = parse(proc.stdout)
        except ExpatError as e:
            return None
        finally:
            proc.wait()
        return xml_el

    def ls(self, rev="HEAD"):
        xml_el = self._get_xml(["svn", "--xml", "ls", "{0}@{1}".format(self.url, rev)])
        for el in xml_el.getElementsByTagName("entry"):
            f = {}
            f["name"] = el.getElementsByTagName("name")[0].firstChild.nodeValue
            f["size"] = int(el.getElementsByTagName("size")[0].firstChild.nodeValue)
            yield f

    def info(self, rev="HEAD"):
        xml_el = self._get_xml(["svn", "--xml", "info", "{0}@{1}".format(self.url, rev)])
        info = {}
        info["rev"] = int(xml_el.getElementsByTagName("commit")[0].getAttribute("revision"))
        return info
