#!/usr/bin/python
import couchdb
from time import time, sleep
import random
import json
from uuid import uuid4
import sys
server = sys.argv[1]
couch = couchdb.Server("http://" + server + ":5984")

print "Will delete current DB! You have 5 seconds to stop me!"
sleep(5)
couch.delete('words')
couch.delete('words_slave')

db = couch.create('words')

print "================\nRev: 0"
a = " "
for word in open("words.txt", "r").readlines():
    word = word.strip()
    doc = {'_id': uuid4().hex, 'word': word, 'cap': word[0], 'len': len(word), 'rev': word[::-1], 't': time()}
    db.save(doc)
    if word[0] != a:
        print word + " saved"
        a = word[0]


for i in range(7):
    print "================\nRev: " + str(i + 1)
    db = couch['words']
    for docid in db:
        doc = db[docid]
        c = chr(random.randint(65,100))
        doc['word'] += c
        doc['len'] += 1
        doc['rev'] = c + doc['rev']
        doc['t'] = time()
        db.save(doc)
        if word[0] != a:
            print word + " saved"
            a = word[0]

print "===============\nReplicate"
couch.create("words_slave")
print couch.replicate("words", "words_slave")

db = (couch['words'], couch['words_slave'])

print "===============\nBreaking repl"
for i in range(3):
    for docid in db[0]:
        choice = random.randint(0, 1)
        doc = db[choice][docid]
        c = chr(random.randint(65,100))
        doc['word'] += c
        doc['len'] += 1
        doc['rev'] = c + doc['rev']
        doc['t'] = time()
        db[choice].save(doc)


print "===============\nGenerate etalon.json"
etalon=[]
for doc_id in db[0]:
    doc1 = db[0][doc_id]
    doc2 = db[1][doc_id]
    etalon.append(doc1 if doc1['t'] > doc2['t'] else doc2)

json.dump(etalon, open("etalon.json", "w"))
print "===============\netalon.json generated"
print "copy it to checker's directory"
print "===============\nWARNING: remove etalon.json from image!"

