from typing import Dict, List, Union, Set
from file_loader import FileLoader
from languagetools import LanguageTools
from enum import IntEnum


class WordType(IntEnum):
    food = 0
    english = 1
    unknown = 2
    brand = 4


class WordSet:

    def __init__(self, is_stats = True):
        self._setup_word_type()
        self._STEMMED_WORDS: Dict = {}
        self._BRANDS: Set = set()
        self._STEMMED_WORDS_FREQ: Dict = {}
        self.is_stats = is_stats

    def add_word_freq(self, stemmed: str, quantified_val: int):
        if stemmed not in self._STEMMED_WORDS_FREQ:
            self._STEMMED_WORDS_FREQ[stemmed] = {'pfreq': 0, 'nfreq': 0, 'bfreq': 0}
        if quantified_val == 1:
            self._STEMMED_WORDS_FREQ[stemmed]['pfreq'] += 1
        elif quantified_val == -1:
            self._STEMMED_WORDS_FREQ[stemmed]['nfreq'] += 1
        elif quantified_val == 0:
            self._STEMMED_WORDS_FREQ[stemmed]['bfreq'] += 1

    def add_word_stats(self, word: str, stemmed: str, grammar_type: str, quantified_val: int, sid: int,
                 is_compound_part=False):
        if stemmed not in self._STEMMED_WORDS:
            self._init_word(word, stemmed, grammar_type, is_compound_part)

        self._STEMMED_WORDS[stemmed]['freq'] += 1

        if quantified_val == 1:
            self._STEMMED_WORDS[stemmed]['psid_list'].append(sid)
        elif quantified_val == -1:
            self._STEMMED_WORDS[stemmed]['nsid_list'].append(sid)
        elif quantified_val == 0:
            self._STEMMED_WORDS[stemmed]['bsid_list'].append(sid)

        if self._STEMMED_WORDS[stemmed]['freq'] > 1:
            self._STEMMED_WORDS[stemmed]['is_unique'] = False

        self._find_set_word_type(stemmed)

    def add_word(self, word: str, stemmed: str, grammar_type: str, quantified_val: int, sid: int, is_compound_part=False):
        if self.is_stats:
            self.add_word_stats(word, stemmed, grammar_type, quantified_val, sid, is_compound_part)
        else:
            self.add_word_freq(stemmed, quantified_val)

    def _init_word(self, word, stemmed, grammar_type, is_compound_part):
        if is_compound_part:
            self._STEMMED_WORDS[stemmed] = {
                'word': word,
                'stemmed': stemmed,
                'w_type': -1,
                'g_type': grammar_type,
                'is_unique': True,
                'is_c_part': True,
                'freq': 0,
                'bsid_list': [],
                'psid_list': [],
                'nsid_list': [],
        }
        else:
            self._STEMMED_WORDS[stemmed] = {
               'word': word,
               'stemmed': stemmed,
               'w_type': -1,
               'g_type': grammar_type,
               'is_unique': True,
                'is_c_part': False,
               'freq': 0,
               'bsid_list': [],
               'psid_list': [],
               'nsid_list': [],
            }

    def _setup_word_type(self):
        self._BRANDS = FileLoader.csv_to_set('\\cache\\usda_db\\BFPD_csv_07132018\\Products.csv', 'manufacturer')

    def set_word_types(self):
        for stemmed in self._STEMMED_WORDS.keys():
            self._find_set_word_type(stemmed)

    def _set_word_type(self, stemmed, val):
        self._STEMMED_WORDS[stemmed]['w_type'] = val

    def _find_set_word_type(self, stemmed: str):
        if LanguageTools.is_word(stemmed):
            if LanguageTools.is_food(stemmed):
                self._set_word_type(stemmed, WordType.food)
            else:
                self._set_word_type(stemmed, WordType.english)
        else:
            if stemmed in self._BRANDS:
                self._set_word_type(stemmed, WordType.brand)
            else:
                self._set_word_type(stemmed, WordType.unknown)

    def get_words_list(self):
        return list(self._STEMMED_WORDS.values())
