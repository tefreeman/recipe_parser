from typing import List, Dict, Tuple, Set
from languagetools import LanguageTools
from enum import IntEnum
from word_set import WordSet


class WordType(IntEnum):
    food = 0
    english = 1
    unknown = 2
    unique = 3
    brand = 4


class Phrase:

    def __init__(self, word_set: WordSet, sid: int):
        self._size: int = 0
        self._word_set: Dict = {}
        self._word_compound_parts_set: Dict = {}
        self._stemmed_word_set: Dict = {}
        self._sid = sid
        self.word_set_class = word_set

    def _get_word_key(self, key):
        if key in self._stemmed_word_set:
            return self._stemmed_word_set[key]
        else:
            return key

    def to_dict(self, word_key) -> Dict:
        key = self._get_word_key(word_key)
        return self._word_set[key]

    def get_size(self):
        return self._size

    def get_all(self) -> List[Dict]:
        return list(self._word_set.values())

    def get(self, i: int):
        if i >= self._size:
            raise Exception('trying to access Phrase index that is out of bounds')
        return self.to_dict(i)

    def add(self, word: str, grammar_type: str):
        stemmed: str = LanguageTools.return_base_word(word, grammar_type)
        self._word_set[word] = {}
        self._word_set[word]['word'] = word
        self._word_set[word]['stemmed'] = stemmed
        self._word_set[word]['type'] = WordType.unknown
        self._word_set[word]['isUnique'] = False
        self._word_set[word]['grammar_type'] = grammar_type
        self._word_set[word]['quantified'] = 0
        self._word_set[word]['pos'] = self._size
        self._stemmed_word_set[stemmed] = word

        self._size += 1

    def replace(self, old_key: str, replace_word: str):
        pos = self._word_set[old_key]['pos']
        self.move_to_compound(old_key)
        self.insert(replace_word, pos)

    def insert(self, word, pos: int, grammar_type='N'):
        stemmed: str = LanguageTools.return_base_word(word, grammar_type)
        self._word_set[word] = {}
        self._word_set[word]['word'] = word
        self._word_set[word]['stemmed'] = stemmed
        self._word_set[word]['grammar_type'] = grammar_type
        self._word_set[word]['quantified'] = 0
        self._word_set[word]['pos'] = pos
        self._stemmed_word_set[stemmed] = word
        self._update_index(pos, is_del=False)
        self._size += 1

    # TODO add deletion of phrase in global phrase dict
    def delete(self, word_key: str):
        if word_key in self._stemmed_word_set:
            word = self._word_set.pop(self._stemmed_word_set[word_key])
            self._stemmed_word_set.pop(word_key)

            self._update_index(word['pos'])
        else:
            try:
                word = self._word_set.pop(word_key)
                self._update_index(word['pos'])
            except:
                print('MAJOR ERROR')
                print('MAJOR ERROR')
                print('MAJOR ERROR')

    def move_to_compound(self, word_key: str):
        key = self._get_word_key(word_key)
        try:
            word = self._word_set.pop(key)
            self._stemmed_word_set.pop(word['stemmed'])
            self._update_index(word['pos'])
            self._word_compound_parts_set[key] = word
        except Exception as e:
            pass

    def _update_index(self, word_key_pos, is_del=True):
        if is_del:
            for key, val in self._word_set.items():
                if val['pos'] >= word_key_pos:
                    word_key_pos = word_key_pos - 1
        else:
            for key, val in self._word_set.items():
                if val['pos'] >= word_key_pos:
                    word_key_pos = word_key_pos + 1

    def set_quantifier(self, word_key, val: int, direction: int):
        key = self._get_word_key(word_key)
        pos = self._word_set[key]['pos']
        words = self.get_words()
        if direction == 1:
            for word in words:
                if word['pos'] == pos+1:
                    if word['quantified'] == 0:
                        word['quantified'] = val
                    else:
                        word['quantified'] *= val

            self.delete(word_key)

        elif direction == -1:
            for word in words:
                if word['pos'] == pos-1:
                    if word['quantified'] == 0:
                        word['quantified'] = val
                    else:
                        word['quantified'] *= val

            self.delete(word_key)

        elif direction == 0:
            self._word_set[word_key]['quantified'] = val

    # TODO auto updating grammar types
    def update_word(self, old_word: str, new_word: str):
        key = self._get_word_key(old_word)
        old_grammar = self._word_set[key]['grammar_type']
        self.delete(old_word)
        self.add(new_word, old_grammar)

    def get_words(self):
        return self._word_set.values()

    # TODO add method to find direction of quant and only apply to word
    def add_words_to_global_dict(self):
        words = self.get_words()
        for word in words:
            self.word_set_class.add_word(word['word'], word['stemmed'], word['grammar_type'], word['quantified'], self._sid)

        for word in self._word_compound_parts_set.values():
            self.word_set_class.add_word(word['word'], word['stemmed'], word['grammar_type'], word['quantified'], self._sid, True)

    def get_text(self, base=True):
        text: str = ""
        words_list = self.get_all()
        if base:
            for i in range(0, self._size - 1):
                text += words_list[i]['stemmed'] + " "
            words_list[self._size - 1]['stemmed'] += text
            return text
        else:
            for i in range(0, self._size - 1):
                text += words_list[i]['word'] + " "
            text += words_list[self._size - 1]['stemmed'] + " "
            return text
