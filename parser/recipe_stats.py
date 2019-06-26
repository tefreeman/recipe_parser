from file_loader import FileLoader
from typing import List, Dict
from pymongo import CursorType
from sentence import IngredientSentence
from word_set import WordSet
from cleaner import Cleaner
from languagetools import LanguageTools


class RecipeStats:
    _recipe_word_set = WordSet(False)
    _freq_stats: Dict = {}

    def __init__(self, db_name: str, col_name: List[str], key_name):
        RecipeStats.load_all_dbs(db_name, col_name, key_name)

    @staticmethod
    def load_all_dbs(db_name: str, col_name: List[str], key_name):
        for collection in col_name:
            cursor = FileLoader.mongo_cursor(db_name, collection)
            RecipeStats.process_collection(key_name, cursor)

    @staticmethod
    def process_collection(key_name, cursor: CursorType):
        i = 0
        for doc in cursor:
            for ingredient in doc[key_name]:
                IngredientSentence(RecipeStats._recipe_word_set, ingredient, doc['_id'])

                i += 1
                test = RecipeStats._recipe_word_set
                print(i)

