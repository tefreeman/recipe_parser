import re
from languagetools import LanguageTools

class Cleaner:

    @staticmethod
    def denoise_string(s: str):
        """
        Denoises the string by removing any characters that aren't word characters or characters that are important
        for detecting ingredients
        :param s:
        :return: s
        """
        s = re.sub(r'[^\u0030-\u0039\u0041-\u005A\u0061-\u007A\u00BC-\u00BE\u00c0-\u02b8\u2150-\u215E ,%\/ .]', ' ', s)  # TODO check to make sure this is not deleting anything important
        s = re.sub(r'\.(?!\d+)', ' ', s) # negative lookahead removes decimals not followed by a number
        s = re.sub(r' +', ' ', s)
        return s.strip().lower()

    @staticmethod
    def clean_manufacturer(s: str):
        return re.sub(r'[^\u0030-\u0039\u0041-\u005A\u0061-\u007A\u00BC-\u00BE\u00c0-\u02b8\u2150-\u215E %\/ ]', ' ', s)


