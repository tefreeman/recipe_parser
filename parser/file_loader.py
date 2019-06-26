import csv
import re
from typing import Dict, List, Set, Tuple
from db_manager import DbManager
from pymongo import CursorType



class FileLoader:
    _base_url = 'C:\\Users\\trevo\\PycharmProjects\\untitled\\commoncrawl\\'

    def __init__(self):
        pass

    @staticmethod
    def get_file_path(path: str) -> str:
        return FileLoader._base_url + path

    @staticmethod
    def csv_to_set(rel_file_path, key: str, encoding_type='utf-8') -> Set[str]:
        r_set: Set[str] = set()
        file_path = FileLoader.get_file_path(rel_file_path)
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r_set.add(row[key].lower())
                except:
                    print('exception')
            return r_set

    @staticmethod
    def csv_to_list(rel_file_path, encoding_type='utf-8') -> List:
        r_list: list = []
        file_path = FileLoader.get_file_path(rel_file_path)
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r_list.append(row)
                except:
                    print('exception')
            return r_list


    @staticmethod
    def mongo_to_set(db_name: str, col_name: str, key: str) -> Set[str]:
        r_set: Set[str] = set()
        db = DbManager(db_name, col_name)
        docs = db.get_all()
        for doc in docs:
            r_set.add(doc[key].lower())
        return r_set


    @staticmethod
    def mongo_cursor(db_name: str, col_name: str) -> CursorType:
        db = DbManager(db_name, col_name)
        return db.get_all_as_cursor()
