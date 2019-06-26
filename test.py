from mongo_collection_stats import return_db_prop_to_set
from data_loader import RecipeDataLoader
from finder import Finder
from mongo_collection_stats import count_letters, return_cross_db_stats, count_words
from typing import List, Dict, Set
from collections import OrderedDict
from languagetools import LanguageTools
from quantifier import Quantifier
import pprint
from sentence import IngredientSentence
from word_set import WordSet
from processor import ProcessIngredients, ProcessRecipes
from recipe_stats import RecipeStats
from measurements import Measurements


new = ProcessRecipes('recipes', 'all', 'recipes', 'processed')
new.process_all()
new.save_all('ingredients', 'processed')

test_dictionary = LanguageTools()
data = RecipeDataLoader(test_dictionary)
finder = Finder()
paths_test: Dict = {}
paths_sorted: List = []
