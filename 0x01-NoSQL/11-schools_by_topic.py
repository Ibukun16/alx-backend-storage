#!/usr/bin/env python3
"""
Write a Python function that returns the list of school having a specific topic
"""


import pymongo


def schools_by_topic(mongo_collection, topic):
    """Python function that returns the list of school having a specific topic
    Args:
    mongo_collection: The pymongo collection object.
    topic (str): The topic to search for.

    Returns:
    List of schools that contain the specified topic.
    """
    filter = {
            'topics': {
                '$elemMatch': {
                    '$eq': topic,
                    },
                },
            }
    return [doc for doc in mongo_collection.find(filter)]
