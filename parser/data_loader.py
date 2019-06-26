import csv
import re
from typing import Dict, List, Set, Tuple
from mongo_collection_stats import return_db_prop_to_set
from wordlet import WordClass
from measurements import Measurements
from cleaner import Cleaner
from languagetools import LanguageTools
from nltk.tokenize import word_tokenize
from itertools import permutations
from quantifier import Quantifier


class RecipeDataLoader:

    base_url = 'C:\\Users\\trevo\\PycharmProjects\\untitled\\commoncrawl\\'
    english_type_dict = {}
    measurements = set()
    prep_methods = set()
    foodb_ingredients = set()
    brands: Set = set()
    words_count: Dict = {}
    raw_ingredients_look_up = {}
    raw_ingredients_data = {}
    processed_ingredients_look_up = {}
    processed_ingredients_data = {}

    #TODO add more possible brands to brands dict
    def __init__(self, dictionary: LanguageTools):
        # self.english_type_dict: Dict = self._load_dictionary(self.base_url + '\\cache\\dictionary\\pg29765.txt') # from english dict
        self.measurements: Measurements = Measurements()
        # self.nutri_brands: Set = return_db_prop_to_set('nutritionix', 'grocery', 'name')
        self.foodb_ingredients: Dict = RecipeDataLoader._load_csv_to_set(self.base_url + 'cache\\usda_db\\foodb_2017_06_29_csv\\food1.csv', 'orig_food_common_name')
        RecipeDataLoader.brands: Dict = RecipeDataLoader._load_csv_to_set(self.base_url + '\\cache\\usda_db\\BFPD_csv_07132018\\Products.csv', 'manufacturer' )
        # self.raw_ingredients_freq = RecipeDataLoader.generate_freq_distribution(self.base_url + '\\cache\\usda_db\\sr28asc\\FOOD_DES.csv', 'Long_Desc')
        #self.raw_ingredients_look_up: Dict = self.create_csv_parse_words(self.base_url + '\\cache\\usda_db\\sr28asc\\FOOD_DES.csv', 'Long_Desc', 'NDB_No')
        self.raw_ingredients_data: Dict = self._load_csv_to_dict(self.base_url + '\\cache\\usda_db\\sr28asc\\ABBREV.csv','NDB_No')
        self.processed_ingredients_look_up: Dict = self._load_csv_to_dict_word_tree_brands(self.base_url + '\\cache\\usda_db\\BFPD_csv_07132018\\Products.csv', 'long_name', 'NDB_Number')
        self.processed_ingredients_data: Dict = self._load_csv_to_dict(self.base_url + '\\cache\\usda_db\\BFPD_csv_07132018\\Products.csv', 'long_name')

    def _add_extra_measurements_and_prep(self):
        measurements: set = {'cup', 'teaspoon', 'tablespoon', 'tsp.', 'can', 'tbsp.', 'ounce', 'oz', 'pound',
                                   'lb', 'inch', 'package', 'liter', 'cm', 'feet', 'foot', 'inches', '"', 'bottle', 'pinch', 'ears', 'garnish'}
        prep: set = {'fresh', 'ground', 'chopped', 'large', 'sliced', 'minced', 'juice', 'cut', 'finely',
                                'dried', 'grated', 'powder', 'thinly', 'whole', 'frozen', 'skinned'}

        self.measurements.union(measurements)
        self.prep_methods.union(prep)

    @staticmethod
    def _add_word_to_word_count(word: str):
        if word in RecipeDataLoader.words_count:
            RecipeDataLoader.words_count[word] = 0
        RecipeDataLoader.words_count[word] += 1

    def _load_csv_to_dict_word_tree(self, file_path, find_key, id_key, split_char =',', encoding_type='utf-8') -> dict:
        r_dict = {}
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    text = re.sub('( or )|( and )|( with )', ' ', Cleaner.denoise_string(row[find_key].lower().strip()))
                    words = re.split(r', |,| ', text)
                    length = len(words)
                    for i in range(0, length):
                        if words[i] not in r_dict:
                            r_dict[words[i]] = {'keys_': set([row[id_key]])}
                        else:
                            r_dict[words[i]]['keys_'].add(row[id_key])
                        for j in range(0, length):
                            if j != i:
                                if words[j] not in r_dict[words[i]]:
                                    r_dict[words[i]][words[j]] = {'keys_': set([row[id_key]]), "length": length}
                                else:
                                    r_dict[words[i]][words[j]]['keys_'].add(row[id_key])
                except Exception as err:
                    print('exception', err)
            return r_dict

    @staticmethod
    def generate_freq_distribution(file_path, find_key, encoding_type='utf-8'):
        tokenized_text = []
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = re.sub('( or )|( and )|( with )', ' ', Cleaner.denoise_string(row[find_key].lower().strip()))
                text = re.sub(r', |,| +', ' ', text)
                text_tokens = word_tokenize(text)
                tokenized_text += LanguageTools.remove_stop_words(words=text_tokens)
        dist = LanguageTools.get_probability_dist(tokenized_text)
        return dist

    @staticmethod
    def testing(file_path, find_key, encoding_type='utf-8'):
        r_dict = {}
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = Cleaner.denoise_string(row[find_key].lower().strip())
                tagged_words = LanguageTools.tag_words(text)
                for tagged in tagged_words:
                    if tagged[1] == "CC":
                        if tagged[0] not in r_dict:
                            r_dict[tagged[0]] = 0
                        r_dict[tagged[0]] += 1
        return r_dict

    def _test_load_csv_to_dict_word_tree(self, file_path, find_key, id_key, split_char=',', encoding_type='utf-8') -> dict:
        total_success = 0
        total_failures = 0
        r_dict = {'organism.n.01': {}, 'food.n.01': {}, 'food.n.02': {}, 'fat.n.01': {}}
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                num_matches = 0
                text = re.sub(r', |,| +', ' ', Cleaner.denoise_string(row[find_key].lower().strip()))
                raw_words = LanguageTools.tag_words(text)
                words = LanguageTools.remove_stop_words(tagged_words=raw_words)
                length = len(words)

                perm = permutations(words)
                for word_tuple in list(perm):
                    text = ""
                    for word in word_tuple:
                        text += LanguageTools.return_base_word(word[0], word[1]) + "_"
                    text = text[0:len(text)-1]
                    if LanguageTools.is_word(text):
                        words.append((text, 'N'))

                for i in range(0, length):
                    word_type = words[i][1]
                    word = LanguageTools.return_base_word(words[i][0], word_type)
                    num_matches += LanguageTools.if_child_add_children(row[id_key], word, word_type, r_dict)
                if num_matches == 0:
                    total_failures += 1
                else:
                    total_success += 1
            return r_dict

    def create_csv_parse_words(self, file_path, find_key, id_key, split_char=',', encoding_type='utf-8') -> dict:
        list_to_write: List = [[id_key, 'words', 'unknowns']]
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            i = 0
            for row in reader:
                text = Cleaner.denoise_string(row[find_key].lower().strip())
                text = Quantifier.normalize_quantifiers(text)
                raw_words = LanguageTools.tag_words(text)
                words_sets = LanguageTools.get_min_words(raw_words)
                list_to_write.append([row[id_key], words_sets[0], words_sets[1]])
                i += 1
                print(i)
        f.close()
        with open('test.csv', 'w',newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(list_to_write)
        writeFile.close()

    def _load_csv_to_dict_word_tree_brands(self, file_path, find_key, id_key, split_char =',', encoding_type='utf-8') -> dict:
        r_dict = {}
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    words = re.split(r', +| +|,', row[find_key])
                    brand = Cleaner.clean_manufacturer(row['manufacturer'])
                    length = len(words)
                    if brand not in r_dict:
                        r_dict[brand] = {'keys_': set([row[id_key]])}
                    else:
                        r_dict[brand]['keys_'].add(row[id_key])
                    for i in range(0, length):
                        if words[i] not in r_dict[brand]:
                            r_dict[brand][words[i]] = set([row[id_key]])
                        else:
                            r_dict[brand][words[i]].add(row[id_key])
                except Exception as err:
                    print('exception', err)
            return r_dict

    def _load_csv_to_dict(self, file_path, id_key, encoding_type='utf-8') -> dict:
        r_dict = {}
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r_dict[row[id_key].lower()] = row
                except:
                    print('exception')
            return r_dict

    # TODO modify to multi-d list to track the next words count to determine main ingredient more accuartly
    def _load_csv_to_set(self, file_path, id_key, encoding_type = "utf-8", dictionary: LanguageTools = None) -> Dict:
        r_dict: Dict = {}
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    text = re.sub(r'\(var.\)', '', row[id_key])
                    text = re.sub(r'\w+\.(?!\d+)', ' ', text)
                    text = re.sub(r'[\(\),"]', ' ', text)
                    words = re.split(r'\/| +', text)
                    full_text = ""
                    for word in words:
                        w = dictionary.return_base_word(word.strip().lower(), 'N')
                        full_text += w + " "
                        if w not in r_dict:
                            r_dict[w] = 0
                        r_dict[w] += 1
                    full_text = full_text.strip()
                    if full_text not in r_dict:
                        r_dict[full_text] = 0
                    r_dict[full_text] += 1


                except:
                    print('exception')

            return r_dict

    def _clean_load_foodb_to_dict(self, file_path, id_key, encoding_type = "utf-8") -> set:
        r_dict = set()
        with open(file_path, 'r', encoding=encoding_type) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r_dict.add(row[id_key].lower())
                except:
                    print('exception')
            return r_dict

    def _load_dictionary(self, dict_path: str) -> dict:
        word_class_keys: dict = {'prep.': WordClass.preposition_or_subordinating_conjunction, 'v.': WordClass.verb_base, 'a.': WordClass.adjective, 'adv.': WordClass.adverb, 'n.': WordClass.noun_plural, 'pron.': WordClass.proper_noun_plural, 'conj.': WordClass.coordinating_conjunction}
        r_dict: Dict = {}
        with open(dict_path, 'r', ) as f:
            line = f.readline()
            while line:
                if re.fullmatch(r'[A-Z;\- ]+\n', line):
                    stripped = line.strip().lower()
                    words = stripped.strip().split(';')
                    line = f.readline()
                    word_class_type = ""
                    stripped = line.strip().lower()

                    st = 'pl. '
                    plural_start = stripped.find(st)
                    if plural_start != -1:
                        part_string = stripped[plural_start+len(st):]
                        result = re.search(r'\A[A-Za-z]{2,}\.', part_string)
                        if result:
                            words.append(result.group(0)[:len(result.group(0))-1])

                    for key, val in word_class_keys.items():
                        if stripped.find(key) != -1:
                            word_class_type = val
                            break

                    if word_class_type != "":
                        for word in words:
                            if word not in r_dict:
                                r_dict[word] = set()
                            r_dict[word].add(word_class_type)

                line = f.readline()
        return r_dict
