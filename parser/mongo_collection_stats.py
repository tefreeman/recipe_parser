import pymongo
from typing import Callable, List, Dict, Set
from collections import OrderedDict
from operator import itemgetter


def return_db_prop_to_set(db_name, col_name: str, key_prop) -> Set:
    r_set: Set = set()
    client = pymongo.MongoClient("mongodb://admin:***REMOVED***@71.91.24.96:27017/")
    db_list = client.list_database_names()

    if db_name not in db_list:
        raise Exception('The given db name does not exist')

    db = client[db_name]
    collection = db[col_name]

    cursor = collection.find({})

    for doc in cursor:
        r_set.add(str(doc[key_prop]).lower())

    return r_set


def return_cross_db_stats(db_name, key_prop, func: Callable[[any, dict, str], None]):
    results: dict = {}
    client = pymongo.MongoClient("mongodb://admin:***REMOVED***@71.91.24.96:27017/")
    db_list = client.list_database_names()

    if db_name not in db_list:
        raise Exception('The given db name does not exist')

    db = client[db_name]
    collections = db.list_collections()

    results['total'] = {}
    for col in collections:
        collection_dict: dict = {}
        collection = db[col['name']]
        cursor = collection.find({}).limit(100)
        func(cursor, collection_dict, key_prop)
        merge_add_dicts(results['total'], collection_dict)
        results[col['name']] = collection_dict

    sort_dict(results)
    return results


def sort_dict(d: dict):
    for domain in d.items():
        d[domain[0]] = OrderedDict(sorted(d[domain[0]].items(), reverse=True))


def merge_add_dicts(base_dict: dict, merge_dict: dict,):
    for key, d_val in merge_dict.items():
        if key not in base_dict:
            base_dict[key] = {'value': 0, 'ids': set()}
        base_dict[key]['value'] += d_val['value']
        base_dict[key]['ids'].union(d_val['ids'])


# TODO change to work like letters does not work currently
def count_keys(cursor: pymongo.cursor, r_dict: dict, key_prop):
    for doc in cursor:
        if isinstance(doc[key_prop], list):
            for data in doc[key_prop]:
                if data not in r_dict:
                    r_dict[data] = {'value': 0, 'ids': set()}
                r_dict[data]['value'] += 1
                r_dict[data]['ids'].add(doc['_id'])
        elif isinstance(doc[key_prop], int):
            data = str(doc[key_prop])
            if data not in r_dict:
                r_dict[data] = {'value': 0, 'ids': set()}
            r_dict[data]['value'] += 1
            r_dict[data]['ids'].add(doc['_id'])
        elif isinstance(doc[key_prop], str):
            data = doc[key_prop]
            if data not in r_dict:
                r_dict[data] = {'value': 0, 'ids': set()}
            r_dict[data]['value'] += 1
            r_dict[data]['ids'].add(doc['_id'])
    return


def count_letters(cursor: pymongo.cursor, r_dict: dict, key_prop):
    for doc in cursor:
        if isinstance(doc[key_prop], list):
            for data in doc[key_prop]:
                for i in range(0, len(data)):
                    if data[i] not in r_dict:
                        r_dict[data[i]] = {'value': 0, 'ids': set()}
                    r_dict[data[i]]['value'] += 1
                    r_dict[data[i]]['ids'].add(doc['_id'])
        elif isinstance(doc[key_prop], int):
            data = str(doc[key_prop])
            for i in range(0, len(data)):
                if data[i] not in r_dict:
                    r_dict[data[i]] = {'value': 0, 'ids': set()}
                r_dict[data[i]]['value'] += 1
                r_dict[data[i]]['ids'].add(doc['_id'])
        elif isinstance(doc[key_prop], str):
            data = doc[key_prop]
            for i in range(0, len(data)):
                if data[i] not in r_dict:
                    r_dict[data[i]] = {'value': 0, 'ids': set()}
                r_dict[data[i]]['value'] += 1
                r_dict[data[i]]['ids'].add(doc['_id'])
    return


def count_words(cursor: pymongo.cursor, r_dict: dict, key_prop):
    for doc in cursor:
        for sentence in doc[key_prop]:
            words = sentence.split(' ')
            for data in words:
                if data not in r_dict:
                    r_dict[data] = 0
                r_dict[data] += 1