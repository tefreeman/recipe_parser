import re
from typing import List, Dict, Set
from wordlet import Wordlet, WordValueType, WordClass


class Finder:
    comma_split_greedy_spaces = re.compile(r', *')
    _r_number = re.compile(r'\d*')
    _r_fraction = re.compile(r'\d+\/\d+')
    _r_float = re.compile(r'\d+\.\d+')
    r_spaces = re.compile(r' +')
    _fraction_keys: Dict = {'½': 0.5, '⅓':  0.333, '⅔': 0.666, '¼': 0.25,'¾': 0.75, '⅕': 0.2, '⅖': 0.4, '⅗': 0.6,
                            '⅘': 0.8, '⅙': 0.5, '⅚': 0.833, '⅜': 0.375, '⅛': 0.125}

    # returns matches
    @staticmethod
    def find_numbers(r: List[Wordlet]) -> int:
        num_key_strings = {'one': 1, 'two': 2, 'three': 3, 'four': 4,'five': 5,'six': 6,'seven': 7,'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'dozen': 12, 'halfadozen': 6, 'halfdozen': 6, 'half-dozen': 6}
        length = len(r)
        matches = 0
        for i in range(0, length):
            if r[i].get_word_type() is WordClass.cardinal_digit:
                word_text = r[i].get_word()
                if word_text in num_key_strings:
                    r[i].set_val(float(num_key_strings[word_text]))
                    r[i].set_type(WordValueType.number)
                    matches += 1
                    continue
                match = re.fullmatch(Finder._r_number, word_text)
                if match:
                    r[i].set_val(float(word_text))
                    r[i].set_type(WordValueType.number)
                    matches += 1
                    continue
                match = re.fullmatch(Finder._r_fraction,  word_text)
                if match:
                    parts = word_text.split('/')
                    r[i].set_val(float(parts[0]) / float(parts[1]))
                    r[i].set_type(WordValueType.number)
                    matches += 1
                    continue
                match = re.fullmatch(Finder._r_float,  word_text)
                if match:
                    r[i].set_val(float(word_text))
                    r[i].set_type(WordValueType.number)
                    matches += 1
                    continue
                if word_text in Finder._fraction_keys:
                    matches += 1
                    r[i].set_val(float(Finder._fraction_keys[s[i]]))
                    r[i].set_type(WordValueType.number)

        return matches

    @staticmethod
    def find_key(s: List[str], r: List[Wordlet]) -> int:
        pass

    @staticmethod
    def find_by_dict_keys(s: List[str], keys: Dict):
        length = len(s)
        for i in range(0, length):
            if s[i] in keys:
                return keys[s[i]]
        return None


