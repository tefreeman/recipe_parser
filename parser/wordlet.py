from enum import IntEnum, Enum
from typing import Set, Union, Tuple


class WordValueType(IntEnum):
    unknown = 0
    m_type = 1
    m_val = 2
    i_name = 3
    i_mod = 4
    i_brand = 5
    prep_type = 6
    number = 7


class WordClass(Enum):
    coordinating_conjunction = "CC"
    cardinal_digit = "CD"
    determiner = "DT"
    existential_there = "EX"
    foreign_word = "FW"
    preposition_or_subordinating_conjunction = "IN"
    adjective = "JJ"
    adjective_comparative = "JJR"
    adjective_superlative = "JJS"
    list_marker = "LS"
    modal = "MD"
    noun_singular = "NN"
    noun_plural = "NNS"
    proper_noun_singular = "NNP"
    proper_noun_plural = "NNPS"
    predeterminer = "PDT"
    possessive_ending = "POS"
    personal_pronoun = "PRP"
    possessive_pronoun = "PRP$"
    adverb = "RB"
    adverb_comparative = "RBR"
    adverb_superlative = "RBS"
    particle = "RP"
    to = "TO"
    interjection = "UH"
    verb_base = "VB"
    verb_past = "VBD"
    verb_gerund_present_participle = "VBG"
    verb_past_participle = "VBN"
    verb_present = "VBP"
    verb_3rd_person = "VBZ"
    wh_determiner = "WDT"
    wh_pronoun = "WP"
    possessive_wh_pronoun = "WP$"
    wh_adverb = "WRB"


class Wordlet:
    def __init__(self, word_str: Tuple[str, str], stem: str, pos: int):
        self.word: str = word_str[0]
        self.word_type: WordClass = WordClass(word_str[1])
        self.stem: str = stem
        self.pos = pos
        self.type: WordValueType = WordValueType.unknown
        self.value: any = None

    def get_word(self):
        return self.word

    def get_stem(self):
        return self.stem

    def get_pos(self):
        return self.pos

    def get_type(self) -> WordClass:
        return self.type

    def set_type(self, type_: WordValueType):
        self.type = type_

    def set_val(self, val):
        self.value = val

    def get_val(self):
        return self.value

    def get_word_type(self):
        return self.word_type
