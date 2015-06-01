#!/usr/bin/env python3

import pymongo
import json
import sys

def main():
    #client = pymongo.MongoClient(host=("localhost:1337","localhost:1338", "localhost:1339"))
    #client = pymongo.MongoClient(host=("localhost"))
    client = pymongo.MongoClient(host=("localhost:1339"))
    db = client.root
    collection = db.features

    print("Load json")
    data = json.load(sys.stdin)
    print("Push to Mongo")
    for feature in data["features"]:
        collection.insert(feature)

if __name__ == "__main__":
    main()
