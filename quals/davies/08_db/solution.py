#!/usr/bin/env python2
# coding=utf-8
__author__ = 'muzafarov'
import couchdb
import sys

server = sys.argv[1]
couch = couchdb.Server("http://%s:5984" % server)
db = (couch['words'], couch['words_slave'])
etalon=[]
for doc_id in db[0]:
    print doc_id
    doc1 = db[0][doc_id]
    doc2 = db[1][doc_id]
    etalon.append(doc1 if doc1['t'] > doc2['t'] else doc2)

couch.delete('words')
couch.delete('words_slave')

db = couch.create('words')
for doc in etalon:
    db.save(doc)

couch.create("words_slave")
couch.replicate("words", "words_slave")
