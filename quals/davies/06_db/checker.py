#!/usr/bin/env python2
# coding=utf-8
__author__ = 'muzafarov'
import couchdb
import sys
import json
import os
from multiprocessing import Pool
OK = 10
FAIL = 11
SERVER = None

class CheckDoc(object):
    def __init__(self):
        self.couch = None

    def __call__(self, doc):
        if self.couch is None:
            self.couch = couchdb.Server("http://%s:5984" % SERVER)

        docid = doc['_id']
        db = (self.couch['words'], self.couch['words_slave'])
        doc1 = db[0][docid]
        doc2 = db[1][docid]
        if doc['t'] != doc1['t'] or doc1['t'] != doc2['t']:
            #print >>sys.stderr, "{0}\n{1}\n{2}".format(doc, doc1, doc2)
            return (FAIL, "Err with doc: {0}".format(docid), (doc, doc1, doc2))

        if doc['word'] != doc1['word'] or doc1['word'] != doc2['word']:
            #print >>sys.stderr, "{0}\n{1}\n{2}".format(doc, doc1, doc2)
            return (FAIL, "Err with doc: {0}".format(docid), (doc, doc1, doc2))

        return (OK, OK, OK)


def check_database(server):
    try:
        etalon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "etalon.json")
        etalon = json.load(open(etalon_path, "r"))
        couch = couchdb.Server("http://%s:5984" % server)
        db = (couch['words'], couch['words_slave'])

        p = Pool(30)
        result = p.map(CheckDoc(), etalon)
        for r in result:
            if r[0] != OK:
                print r[1]
                print >>sys.stderr, r[2]
                return FAIL

        return OK

    except Exception as e:
        print "Exception: {0}".format(e)
        return FAIL

if __name__ == '__main__':
    server = sys.argv[1]
    SERVER = server
    sys.exit(check_database(server))
