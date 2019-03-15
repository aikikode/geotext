# -*- coding: utf-8 -*-
import re
import sys

from unidecode import unidecode


def get_words_counts(phrases_list):
    """
    Set of phrases lengths
    e.g.
    get_words_count(['hello', 'hi']) -> {1,}
    get_words_count(['hello', 'hi', 'hello, world and all']) -> {1, 4}
    """
    return set(map(len, map(lambda phrase: phrase.split(), phrases_list)))


def replace_non_ascii(text):
    if sys.version_info < (3, 0):
        to_unicode = unicode  # noqa
        if type(text) == to_unicode:
            return unidecode(text)
        return unidecode(to_unicode(text, encoding='utf-8'))
    else:
        return unidecode(text)


def fix_location_name(name):
    return re.sub(' city$', '', name, flags=re.IGNORECASE)


def canonize_location_name(name):
    canonized_name = fix_location_name(name).lower()
    # Remove dots and strip all non-ascii:
    # ("Washington, D.C." -> "Washington DC")
    return re.sub(
        r'[,:;\'\" ]+', ' ', re.sub(r'\.', '', canonized_name)
    ).strip()
