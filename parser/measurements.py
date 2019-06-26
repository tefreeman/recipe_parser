from typing import List, Dict, Set, Tuple
from collections import OrderedDict
from languagetools import LanguageTools
from measurement.measures import Weight, Volume, Distance
from enum import Enum
from word2number import w2n
from measurement.utils import guess
from wordlet import WordClass
from enum import Enum


class MeasurementClassType(Enum):
    VOLUME = 0
    WEIGHT = 1
    DISTANCE = 2
    CONTAINER = 3
    UNKNOWN = 4


class Measurements:
    _unit_measurement = {'unit_of_measurement.n.01', 'measure.n.02'}
    _unit_volume = {'volume_unit.n.01'}
    _unit_weight = {'weight_unit.n.01'}
    _unit_distance = {'linear_unit.n.01'}
    _unit_container = {'container.n.01'}
    _volume_conversion = {'cup': 'us_cup', 'quart': 'us_qt', 'pint': 'us_pint', 'ounce': 'us_oz', 'oz': 'us_oz',
                          'fl oz': 'us_oz','fluid ounce': 'us_oz', 'gallon': 'us_g','tablespoon': 'us_tbsp',
                          'tbsp': 'us_tbsp', 'teaspoon': 'us_tsp', 'tsp': 'us_tsp', 'liter': 'l','milliliter': 'ml',
                          'ml': 'ml'}
    _weight_conversion = {'milligram': 'mg', 'mg': 'mg', 'gram': 'g', 'g': 'g', 'lb': 'lb', 'pound': 'lb',
                          'kilogram': 'kg', 'kg': 'kg', 'mcg': 'mcg', 'ounce': 'oz', 'oz': 'oz'}

    _distance_conversion = {'cm': 'cm', 'centimeter': 'cm', 'inch': 'inch', 'inches': 'inch', 'foot': 'ft', 'ft': 'ft',
                            'feet': 'ft', 'yard': 'yard', 'meter': 'm', 'm': 'meter'}

    _extra_possible_nums: Dict = {'dozen': 12, '½': 0.5, '⅓': 0.333, '⅔': 0.666, '¼': 0.25, '¾': 0.75, '⅕': 0.2, '⅖': 0.4, '⅗': 0.6,
                            '⅘': 0.8, '⅙': 0.5, '⅚': 0.833, '⅜': 0.375, '⅛': 0.125}

    def __init__(self):
        pass

    @staticmethod
    def is_measurement(word, word_type):
        return LanguageTools.is_in_tree(word, word_type, Measurements._unit_measurement)

    @staticmethod
    def extract_measurements(tagged_word_list: List[Tuple[str, str]]):
        measurements = []
        length = len(tagged_word_list)
        deletions = []
        prev_pos = 0
        for i in range(0, length):
            word = LanguageTools.return_base_word(tagged_word_list[i][0], tagged_word_list[i][1])
            word_type = tagged_word_list[i][1]
            measurement_set = Measurements.get_measurement_class(word, word_type)

            if len(measurement_set) > 0:
                m_set: List = []
                deletions.append(i)
                result = Measurements._extract_numerical_data(tagged_word_list[prev_pos:i])
                for measurement_item in measurement_set:
                    m_set.append(Measurements.get_measurement(word, measurement_item, result[0]))

                measurements.append(m_set)  
                for deletion in result[1]:
                    deletions.append(deletion + prev_pos)

                prev_pos = i

        deletions.sort(reverse=True)
        deletions = Measurements._duplicate_remove(deletions)
        for dels in deletions:
            tagged_word_list.pop(dels)

        return measurements

    @staticmethod
    def _duplicate_remove(duplicate):
        final_list = []
        for num in duplicate:
            if num not in final_list:
                final_list.append(num)
        return final_list

    @staticmethod
    def _extract_numerical_data(tagged_word_list: List[Tuple[any, any]]):
        length = len(tagged_word_list)
        numbers = []
        deletion_list = []

        started = False
        for i in range(0, length):
            word = tagged_word_list[i][0]
            word_type = tagged_word_list[i][1]

            if word_type == WordClass.cardinal_digit.value:
                started = True
                numbers.append(Measurements._convert_to_number(word))
                deletion_list.append(i)
            elif started:
                if word == ',':
                    numbers.append(',')
                    deletion_list.append(i)
                elif word == 'to' or word == 'or':
                    numbers.append('to')
                    deletion_list.append(i)
                else:
                    break

        numbers_length = len(numbers)
        if numbers_length == 0:
            return 1, deletion_list
        elif numbers_length == 1:
            return numbers[0], deletion_list
        else:
            for j in range(0, numbers_length):
                if j+1 < numbers_length:
                    if isinstance(numbers[j], (int, float)) and isinstance(numbers[j+1], float):
                        if numbers[j+1] < 1:
                            numbers[j] += numbers[j+1]
                            numbers.pop(j+1)
            j = 0
            for j in range(0, numbers_length):
                if j+2 < numbers_length:
                    if isinstance(numbers[j], (int, float)) and numbers[j+1] == ',' and isinstance(numbers[j+2], (int, float)):
                            numbers[j] *= numbers[j+2]
                            numbers.pop(j+2)
                            numbers.pop(j+1)
                    elif isinstance(numbers[j], (int, float)) and numbers[j+1] == 'to' and isinstance(numbers[j+2], (int, float)):
                        numbers[j] = (numbers[j] + numbers[j+2]) / 2
                        numbers.pop(j + 1)
                        numbers.pop(j + 2)
            return numbers[0], deletion_list


    @staticmethod
    def get_measurement_class(word, word_type):
        r_set: Set = set()
        if LanguageTools.is_in_tree(word, word_type, Measurements._unit_measurement):
            if word in Measurements._volume_conversion:
                r_set.add(MeasurementClassType.VOLUME)
            if word in Measurements._weight_conversion:
                r_set.add(MeasurementClassType.WEIGHT)
            if word in Measurements._distance_conversion:
                r_set.add(MeasurementClassType.DISTANCE)
            if len(r_set) == 0:
                r_set.add(MeasurementClassType.UNKNOWN)
        elif LanguageTools.is_in_tree(word, word_type, Measurements._unit_container):
            r_set.add(MeasurementClassType.CONTAINER)
        else:
            if word in Measurements._volume_conversion:
                r_set.add(MeasurementClassType.VOLUME)
            if word in Measurements._weight_conversion:
                r_set.add(MeasurementClassType.WEIGHT)
            if word in Measurements._distance_conversion:
                r_set.add(MeasurementClassType.DISTANCE)
            if len(r_set) == 0:
                r_set.add(MeasurementClassType.UNKNOWN)
        return r_set

    @staticmethod
    def get_measurement(mid: str, class_type: MeasurementClassType, val):
        if class_type == MeasurementClassType.VOLUME:
            mid = Measurements._volume_conversion[mid]
            return guess(val, mid, measures=[Volume])
        if class_type == MeasurementClassType.WEIGHT:
            mid = Measurements._weight_conversion[mid]
            return guess(val, mid, measures=[Weight])
        if class_type == MeasurementClassType.DISTANCE:
            mid = Measurements._distance_conversion[mid]
            return guess(val, mid, measures=[Distance])
        if class_type == MeasurementClassType.CONTAINER:
            return val

    @staticmethod
    def _convert_to_number(value_str: str):
        num = -1
        try:
            if value_str.find('.') == -1:
                num = int(num)
            else:
                num = float(num)
        except:
            pass

        try:
            num = w2n.word_to_num(value_str)
        except:
            pass
        try:
            if value_str.find('/') != -1:
                nums = value_str.split('/')
                num = float(nums[0]) / float(nums[1])
        except:
            pass
        if value_str in Measurements._extra_possible_nums:
            num = Measurements._extra_possible_nums[value_str]

        if num == -1:
            raise Exception('Number not correctly parsed in convert_to_number function')
        else:
            return num


