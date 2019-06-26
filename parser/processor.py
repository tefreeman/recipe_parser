from file_loader import FileLoader
from sentence import IngredientSentence
from typing import List
from db_manager import DbManager
from word_set import WordSet
from pymongo import CursorType

class ProcessIngredients:
    def __init__(self):
        self.ingredients_set: List = FileLoader.csv_to_list('\\cache\\usda_db\\sr28asc\\FOOD_DES.csv')
        self.ingredient_word_set = WordSet()

    def process_all(self):
        i = 0
        for doc in self.ingredients_set:
            try:
                IngredientSentence(self.ingredient_word_set, doc['Long_Desc'], doc['NDB_No'])
            except:
                pass
            i += 1
            print(i)

    def save_all(self, db_name, col_name):
        print('adding docs')
        db = DbManager(db_name, col_name)
        db.add_docs(self.ingredient_word_set.get_words_list())


class ProcessRecipes:
    def __init__(self, db_name, col_name, save_db_name, save_col_name):
        self.db_save = DbManager(save_db_name, save_col_name)
        self.db = DbManager(db_name, col_name)
        self.recipes_cursor: CursorType = self.db.get_all_as_cursor()
        self.recipes_wordset = WordSet()

    def process_all(self):
        i = 0
        errors = 0
        for doc in self.recipes_cursor:
            try:
                ingredient_data = []
                for ingredient in doc['ingredients']:
                    sent = IngredientSentence(self.recipes_wordset, ingredient, doc['_id'], False)
                    ingredient_data.append(sent.get_all_stemmed_words())
                doc['processed'] = ingredient_data
                self.db_save.add_doc(doc)
                i += 1
                if i % 10000 == 0:
                    print('i: ', i)
            except:
                errors += 1
                print('ERROR', errors)

    def save_all(self, db_name, col_name):
        print('adding docs')
        db = DbManager(db_name, col_name)
        db.add_docs(self.recipes_wordset.get_words_list())

