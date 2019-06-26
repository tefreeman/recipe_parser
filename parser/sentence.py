from typing import List, Union, Tuple, Set, Dict
from cleaner import Cleaner
from languagetools import LanguageTools
from quantifier import Quantifier, Quant
from phrase import Phrase
from word_set import WordSet
from measurements import Measurements


class IngredientSentence:

    def __init__(self, word_set_class: WordSet, text: str, sid: int,  isDb = True):
        self.sid = sid
        self.word_set_class = word_set_class
        self.text = Cleaner.denoise_string(text)
        self.tagged_text: List[Tuple[str, str]] = LanguageTools.tag_words(self.text)
        self.tagged_phrases: List[Phrase] = self.ingredient_to_phrase_list()
        self.normalize_phrases_quantifers()
        self.merge_phrases_with_compounds(LanguageTools.get_min_words(self.tagged_phrases, 3, 7))
        self.remove_blank_phrases()
        if isDb:
            self.add_phrase_to_global_words()

    def get_all_stemmed_words(self):
        r_list = []
        for p in self.tagged_phrases:
            words = p.get_all()
            for word in words:
                r_list.append(word['stemmed'])
        return r_list

    def normalize_phrases_quantifers(self):
        for p in self.tagged_phrases:
            Quantifier.normalize_quantifiers(p)

    def add_phrase_to_global_words(self):
        for phrase in self.tagged_phrases:
            phrase.add_words_to_global_dict()

    def remove_blank_phrases(self):
        for phrase in self.tagged_phrases:
            if phrase.get_size() == 0:
                self.tagged_phrases.remove(phrase)

    def remove_overlapping_compounds(self, compound_words: List[Dict]):
        length = len(compound_words)
        compound_distance: List[Tuple[float, Dict]] = []
        for i in range(0, length):
            compound = compound_words[i]
            avg_dist = 0
            words = compound['words']
            word_length = len(words)
            for j in range(1, word_length):
                avg_dist = words[j]['pos'] - words[j-1]['pos']
            avg_dist = avg_dist / (word_length - 1)
            compound_distance.append((avg_dist, compound))

        compound_distance.sort(key = lambda x: x[0], reverse=True)
        r_compound_words: List[Dict] = []
        used_words: Set = set()
        for i in range(0, length):
            pos = set()
            for word in compound_distance[i][1]['words']:
                pos.add(word['pos'])
            intersection = pos.intersection(used_words)
            if len(intersection) == 0:
                r_compound_words.append(compound_distance[i][1])
                used_words = used_words.union(pos)
        return r_compound_words

    def merge_phrases_with_compounds(self, compound_words: List[Dict]):
        compound_words = self.remove_overlapping_compounds(compound_words)
        words_used: Set = set()
        for compounds in compound_words:
            is_words_used = False
            temp_used = set()
            for word in compounds['words']:
                if word['word'] in words_used:
                    is_words_used = True
                    break
                else:
                    temp_used.add(word['word'])
            if not is_words_used:
                words_used = words_used.union(temp_used)

                for i in range(0, len(compounds['words'])):
                    if i == 0:
                        word = compounds['words'][0]
                        phrase: Phrase = self.tagged_phrases[word['phrase_pos']]
                        phrase.replace(word['word'], compounds['compound_word'])
                    else:
                        word = compounds['words'][i]
                        phrase: Phrase = self.tagged_phrases[word['phrase_pos']]
                        phrase.move_to_compound(word['word'])

    # TODO: add 'or' detection to fire another sentence to be created
    def ingredient_to_phrase_list(self) -> List[Phrase]:
        phrases: List[Phrase] = [Phrase(self.word_set_class, self.sid)]
        count = 0
        for word in self.tagged_text:
            if word[0] == ',' or word[0] == 'and':
                phrases.append(Phrase(self.word_set_class, self.sid))
                count += 1
            elif word[0] == 'or':
                pass
            else:
                phrases[count].add(word[0], word[1])

        return phrases


