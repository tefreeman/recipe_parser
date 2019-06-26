import hunspell
import re
from typing import Dict, List, Set, Tuple
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist, DictionaryProbDist
from nltk.collocations import BigramAssocMeasures, TrigramAssocMeasures, BigramCollocationFinder
import collections

from nltk.stem import PorterStemmer
from itertools import permutations
class LanguageTools:



    food_component_synset_keys = {'food.n.01', 'food.n.02', 'plant.n.02', 'fruit.n.01', 'animal.n.01'}
    just_food_component_synset_keys = {'food.n.01', 'food.n.02'}
    wnl = nltk.WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    hyponyms_memory = {}

    @staticmethod
    def if_child_add_children(uid: str, w: str, w_type: str, compare_synset_keys: Dict) -> int:
        total_matches = 0
        for key, val in compare_synset_keys.items():
            word_synsets = wordnet.synsets(w, LanguageTools._get_wordnet_pos(w_type))
            for word_synset in word_synsets:
                total_matches += LanguageTools._get_path_if_child(uid, word_synset, key, compare_synset_keys)
        return total_matches

    @staticmethod
    def get_prob_normalized(dist: DictionaryProbDist, word: str):
        return dist.prob(word) / dist.prob(dist.max())

    @staticmethod
    def get_trev_word_val_metric(dist: DictionaryProbDist, word: str, word_key: str = None):
        if word_key is not None:
            depth = (LanguageTools.get_max_child_depth(word_key) - 5) / (16-5)
            prob = LanguageTools.get_prob_normalized(dist, word)
            return depth / prob

    @staticmethod
    def get_min_words_by_phrase(phrases: List, max_words_in_compound, max_permutation_size) -> List[Dict]:
        length = len(phrases)
        compound_words: List[Dict] = []
        for pnum in range(0, length):
            words_list: List[Dict] = []
            for word in phrases[pnum].get_all():
                word['phrase_pos'] = pnum
                words_list.append(word)

            for i in range(2, max_words_in_compound + 1):
                perm = permutations(words_list, i)
                LanguageTools._get_compound_words(perm, compound_words)

        compound_words.sort(key=lambda t: len(t['words']), reverse=True)
        return compound_words

    @staticmethod
    def get_min_words(phrases: List, max_words_in_compound, max_permutation_size) -> List[Dict]:
        pos = 0
        loops = 0
        length = len(phrases)
        compound_words: List[Dict] = []
        while pos < length:
            phrase_list: List = []
            words_list: List[Dict] = []
            words_count = 0
            for p in range(pos, length):
                phrase_words_size = phrases[p].get_size()
                if phrase_words_size >= max_permutation_size and len(phrase_list) == 0:
                    phrase_list.append(phrases[p])
                    words_count += phrase_words_size
                    pos += 1
                    for word in phrases[p].get_all():
                        word['phrase_pos'] = p
                        words_list.append(word)

                elif words_count + phrase_words_size < max_permutation_size:
                    phrase_list.append(phrases[p])
                    words_count += phrase_words_size
                    pos += 1

                    for word in phrases[p].get_all():
                        word['phrase_pos'] = p
                        words_list.append(word)
            for i in range(2, max_words_in_compound+1):
                perm = permutations(words_list, i)
                LanguageTools._get_compound_words(perm, compound_words)

            loops += 1
        compound_words.sort(key=lambda t: len(t['words']), reverse=True)
        return compound_words

    @staticmethod
    def _get_compound_words(perm: permutations, compound_words):
        for word_combo in list(perm):
            text = ""
            text_dash = ""
            for word in word_combo:
                text += word['word'] + "_"
                text_dash += word['word'] + "-"
            text = text[0:len(text) - 1]
            text_dash = text_dash[0:len(text_dash) - 1]
            if LanguageTools.is_word(text):
                compound_words.append({'words': word_combo, 'compound_word': text})
            if LanguageTools.is_word(text_dash):
                compound_words.append({'words': word_combo, 'compound_word': text_dash})

    @staticmethod
    def get_probability_dist(word_token_set: List[str]):
        f_dist = FreqDist(word_token_set)
        return DictionaryProbDist(f_dist, normalize=True)

    @staticmethod
    def get_max_child_depth(synset_key: str):
        m_dict: Dict = LanguageTools.hyponyms_memory

        start_word = wordnet.synset(synset_key)
        max_depth = 0

        if start_word in m_dict:
            return m_dict[start_word]
        else:
            max_depth = start_word.min_depth()
            m_dict[start_word.name()] = max_depth

        tree: List = start_word.hyponyms()

        while len(tree) > 0:
            depth = 0
            word = tree.pop()
            if word.name() in m_dict:
                depth = m_dict[word.name()]
            else:
                depth = word.min_depth()
                m_dict[word.name()] = depth
                tree.extend(word.hyponyms())

            if depth > max_depth:
                max_depth = depth

        return max_depth

    @staticmethod
    def is_child(w: str, w_type, compare_synset_keys: Dict) -> bool:
        for key, val in compare_synset_keys.items():
            compare_synset = wordnet.synset(key)
            word_synsets = wordnet.synsets(w, LanguageTools._get_wordnet_pos(w_type))
            compare_depth = compare_synset.min_depth()
            for word_synset in word_synsets:
                if LanguageTools._is_word_in_path(word_synset, key):
                    depth = word_synset.min_depth()
                    if depth > compare_depth:
                        compare_synset_keys[key] = True
                        break

    @staticmethod
    def min_depth(w: str, w_type):
        depth = 100000
        word_synset = wordnet.synsets(w, LanguageTools._get_wordnet_pos(w_type))
        for synset in word_synset:
            n_depth = synset.min_depth()
            if n_depth < depth:
                depth = n_depth
        return depth

    @staticmethod
    def return_base_word(word: str, word_type: str) -> str:
        return LanguageTools.wnl.lemmatize(word, LanguageTools._get_wordnet_pos(word_type))

    @staticmethod
    def return_base_words(tagged_words: List[Tuple[str, str]]) -> List[str]:
        r_list: List[str] = []
        for word in tagged_words:
            r_list.append(LanguageTools.wnl.lemmatize(word[0], LanguageTools._get_wordnet_pos(word[1])))
        return r_list

    @staticmethod
    def get_synonyms(word: str) -> Set[str]:
        r_set: Set = set()
        for synset in wordnet.synsets(word):
            r_set = r_set.union(set(synset.lemma_names()))
        return r_set

    @staticmethod
    def is_food(word: str):
        return LanguageTools._quick_check_base_type(word, 'N', LanguageTools.food_component_synset_keys)

    @staticmethod
    def is_in_tree(word, word_type, synset_keys):
        return LanguageTools._quick_check_base_type(word, word_type, synset_keys)

    @staticmethod
    def compare_words(word: str, word1: str, word_type: str):
        word_synset = wordnet.synsets(word, LanguageTools._get_wordnet_pos(word_type))
        word1_synset = wordnet.synsets(word1, LanguageTools._get_wordnet_pos(word_type))
        highest_match_score = 0.0
        for word_set in word_synset:
            pass

    @staticmethod
    def get_similarity(word: str, word_type, similarity_synset_dict: Set):
        r_dict = {}
        word_synset = wordnet.synsets(word, LanguageTools._get_wordnet_pos(word_type))
        for key in similarity_synset_dict:
             r_dict[key] = LanguageTools._get_similiarity(word_synset, key)

        return r_dict
        print('test')

    @staticmethod
    def _quick_check_base_type(word: str, word_type: str, similarity_synset_dict: Set[str]) -> bool:
        word_synset = wordnet.synsets(word, LanguageTools._get_wordnet_pos(word_type))
        for key in similarity_synset_dict:
            is_in_path = LanguageTools._is_any_form_in_path(word_synset, key)
            if is_in_path:
                return True
        return False

    @staticmethod
    def check_base_type(word: str, word_type: str, similarity_synset_dict: Set[str]):
        r_dict = {}
        word_synset = wordnet.synsets(word, LanguageTools._get_wordnet_pos(word_type))
        for key in similarity_synset_dict:
            r_dict[key] = LanguageTools._is_any_form_in_path(word_synset, key)
        return r_dict

    @staticmethod
    def synset_list_to_name_dict(uid: str, r_dict: Dict, synset_list: List):
        length = len(synset_list)
        pos = r_dict
        for i in range(0, length):
            name = synset_list[i].name()
            if name not in pos:
                pos[name] = {}
            pos = pos[name]
        if 'set' not in pos:
            pos['set'] = set()
        pos['set'].add(uid)

    @staticmethod
    def tokenize(s: str) -> List[str]:
        return word_tokenize(s)

    @staticmethod
    def remove_stop_words(words: List[str] = None, tagged_words: List[Tuple[str, str]] = None, overrides: Set = None) -> List[str]:
        filtered_sentence = []
        user_overrides = set()
        if overrides is not None:
            user_overrides = overrides
        if words is not None:
            for w in words:
                if w not in LanguageTools.stop_words and w not in user_overrides:
                    filtered_sentence.append(w)
        if tagged_words is not None:
            for w in tagged_words:
                if w[0] not in LanguageTools.stop_words and w[0] not in user_overrides:
                    filtered_sentence.append(w)
        return filtered_sentence

    @staticmethod
    def is_word(word: str) -> bool:
        if wordnet.synsets(word):
            return True
        return False

    @staticmethod
    def _get_path_if_child(uid: str, word_synset, synset_parent_name: str, base_dict: Dict) -> int:
        r_dict = base_dict[synset_parent_name]
        paths = word_synset.hypernym_paths()
        total_matches: int = 0
        for path in paths:
            path_length = len(path)
            for i in range(0, path_length):
                if path[i].name() == synset_parent_name:
                    LanguageTools.synset_list_to_name_dict(uid, r_dict, path[i+1:path_length])
                    total_matches += 1
        return total_matches

    @staticmethod
    def _is_word_in_path(word_synset, syset_compare_to: str) -> bool:
        paths = word_synset.hypernym_paths()
        for path in paths:
            for synset in path:
                if synset.name() == syset_compare_to:
                    return True
        return False

    @staticmethod
    def _is_any_form_in_path(word_synset, syset_compare_to: str):
        for word_set in word_synset:
            paths = word_set.hypernym_paths()
            for path in paths:
                for synset in path:
                    if synset.name() == syset_compare_to:
                        return True
        return False

    @staticmethod
    def add_paths_to_dict(word: str, dic: Dict):
        word_synset = wordnet.synsets(word)
        for word_set in word_synset:
            paths = word_set.hypernym_paths()
            for path in paths:
                for synset in path:
                    if synset._name not in dic:
                        dic[synset._name] = 0
                    dic[synset._name] += 1

    @staticmethod
    def _get_similiarity(word_synset, compare_synset_key):
        highest_match_val = 0.0
        for word_set in word_synset:
            val = word_set.path_similarity(wordnet.synset(compare_synset_key))
            if val > highest_match_val:
                highest_match_val = val
        return highest_match_val

    @staticmethod
    def tag_words(words: str) -> List[Tuple[str, str]]:
        tokens = nltk.word_tokenize(words)
        return nltk.pos_tag(tokens)

    @staticmethod
    def _get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        elif treebank_tag.startswith('S'):
            return wordnet.ADJ_SAT
        else:
            return wordnet.NOUN

    @staticmethod
    def verify_words_have_class_type(dictionary: Dict):
        for key, val in dictionary.items():
            if len(val) < 1:
                raise Exception(key + ' did not have a proper word class type')
