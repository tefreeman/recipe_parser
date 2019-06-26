import re
from typing import List, Dict, Set, Tuple, Union
from languagetools import LanguageTools
from phrase import Phrase


class Quant:
    # word : ( pos (3) | neg (-3), before (-1) | after (1) )
    _default_quants = {'with': (1, 1, 'N'), "add": (1, 1, 'N'), "include": (1, 1, 'N'),
                       'without': (-1, 1, 'N'), 'no': (-1, 1, 'N'), 'not': (-1, 1, 'N'), 'free': (-1, -1, 'N'),
                      # 'low': (-2, 1, 'N'), 'reduce': (-2, 1, 'N'), 'little': (-2, 1, 'N'),
                      # 'few': (-2, 1, 'N'), 'high:': (2, 1, 'N'), 'numerous': (2, 1, 'N'), 'plenty': (2, 1, 'N'),
                      # 'lots': (2, 1, 'N')
              }

    _switch_words = {'too': (0, -1)}
    _amount_words = {'half': 0.5, 'double': 2.0, 'triple': 3.0}
    _neg_prefixes = re.compile(r'\A(un|non)')
    _neg_suffixes = re.compile(r'(less|free)$')

    def __init__(self):
        self.quants_ids: Dict[int] = {}
        self.quants: List[Dict] = []
        self._init_default()

    def get(self, word: str):
        if word in self.quants_ids:
            return self.quants[self.quants_ids[word]]
        return None

    def get_id(self, word) -> int:
        if word in self.quants_ids:
            return self.quants_ids[word]
        return None

    def get_by_id(self, i: int):
        return self.quants[i]

    def join(self, quants_ids: List[int], pos_list: List[int]):
        length = len(quants_ids)
        if length == 0:
            return None
        if length == 1:
            quant = self.get_by_id(quants_ids[0])
            quant['pos'] = pos_list[0] - quant['offset']
            return quant
        else:
            init_quant = {'val': 1, 'offset': 0, 'grammar_type': ''}
            for i in quants_ids:
                quant = self.get_by_id(quants_ids[i])
                init_quant['val'] *= quant['val']
                init_quant['grammar_type'] = quant['grammar_type']
                quant['pos'] = pos_list[0] - quant['offset']

        return init_quant

    def _init_default(self):
        i = 0
        for key, val in Quant._default_quants.items():
            self.quants_ids[key] = i
            self.quants.append({'val': val[0], 'offset': val[1], 'grammar_type': val[2]})
            i += 1


class Quantifier:
    @staticmethod
    def normalize_quantifiers(phrase: Phrase):
        quant_class = Quant()
        phrase_list: List = phrase.get_all()
        i = 0

        for item in phrase_list:
            word = item['stemmed']

            result = Quantifier.find_suffix_prefix(word)
            if result:
                phrase.update_word(word, result[1])
                phrase.set_quantifier(result[1], result[0], 0)

            quant = quant_class.get(word)
            if quant:
                phrase.set_quantifier(word, quant['val'], quant['offset'])

            i += 1

    @staticmethod
    def search_word(word: str):
        quant_val = 1
        pre_match = False
        suf_match = False
        neg_pre = list(filter(None, Quant._neg_prefixes.split(word)))
        neg_suf = list(filter(None, Quant._neg_suffixes.split(word)))

        if len(neg_pre) > 1:
            if LanguageTools.is_word(neg_pre[1]):
                quant_val *= -1
                pre_match = True
        if len(neg_suf) > 1:
            if LanguageTools.is_word(neg_suf[0]):
                quant_val *= -1
                suf_match = True

        if not pre_match and not suf_match:
            return None
        elif pre_match and suf_match:
            if neg_pre[1] == neg_suf[0]:
                return [quant_val, neg_pre[1]]
            else:
                raise Exception('neg_pre and neg_suf do not match!!!')
        elif pre_match:
            return [quant_val, neg_pre[1]]
        else:
            return [quant_val, neg_suf[0]]

    @staticmethod
    def find_suffix_prefix(word: str):
        prefix_suffix = Quantifier.search_word(word)
        if not prefix_suffix:
            return None
        else:
            return prefix_suffix[0], prefix_suffix[1]



