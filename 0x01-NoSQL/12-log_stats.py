#!/usr/bin/env python3
"""
a Python script that provides some stats about Nginx logs stored in MongoDB:

Database: logs
Collection: nginx
Display (same as the example):
first line: x logs where x is the number of documents in this collection
second line: Methods:
5 lines with the number of documents with the method =
["GET", "POST", "PUT", "PATCH", "DELETE"] in this order
(see example below - warning: it’s a tabulation before each line)
one line with the number of documents with:
method=GET
path=/status
You can use this dump as data sample: dump.zip
"""


import pymongo
from pymongo import MongoClient


def nginx_log_stats(nginx_collection):
    """Prints stats Nginx request logs."""
    print(f"{nginx_collection.count_documents({})} logs")

    print("Methods:")
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    for method in methods:
        count = len(list(nginx_collection.find({"method": method})))
        print(f"\tmethod {method}: {count}")
    count_status_checked = len(list(nginx_collection.find(
        {"method": "GET", "Path": "/status"}
    )))
    print(f"{count_status_checked} status check")


if __name__ == "__main__":
    mongo_client = MongoClient('mongodb://127.0.0.1:27017/')
    nginx_log_stats(mongo_client.logs.nginx)
