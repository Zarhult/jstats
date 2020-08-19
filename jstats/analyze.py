'''
Module containing functions for generating analytics.
'''

from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from natto import MeCab

Analytics = namedtuple('Analytics', [
    'freq_list',
    'cutoff_dict',
    'total_morphs',
    'total_known_morphs',
    'unique_unknown_morphs'
])
Analytics.__doc__ = '''\
    The Analytics object contains all the data gathered and organized
    from whatever source.

    Attributes:
        freq_list: sorted list of tuples of unknown morpheme/its frequency
        cutoff_dict: a dictionary mapping desired percent comprehension
                     to necessary number of (most common) unique
                     unknown morphemes learned
        total_morphs: total number of morphemes, including duplicates
        total_known_morphs: total number of known morphemes, including
                            duplicates
        unique_unknown_morphs: total number of unique unknown morphemes'''

# Make MeCab output nothing but morphemes
fmt = {'node_format': r'%m\n',
       'bos_format': r'',
       'eos_format': r'',
       'unk_format': r''}

mecab = MeCab(options=fmt)


def is_cjk(char):
    '''Returns whether or not char is a CJK character.'''
    if '\u4E00' <= char <= '\u9FFF':
        return True

    return False


def load_page(url):
    '''Returns html given a URL.'''
    print('Fetching HTML...')
    page = requests.get(url, timeout=5)
    return page.content


def get_soup(html):
    '''Returns parsed soup object given html.'''
    print('Parsing html...')
    # Ignore non UTF-8
    soup = BeautifulSoup(html.decode('utf-8', 'ignore'), 'html.parser')

    print('Removing furigana...')
    for rt_tag in soup.select('rt'):
        rt_tag.extract()

    return soup


def get_morpheme_list(strings):
    '''Returns list of morpheme strings found in list of strings.'''
    morpheme_list = []
    for line in strings:
        # Ignore non-UTF-8 characters/strings
        try:
            tokens = mecab.parse(line)
            tokens = tokens.splitlines()
            morpheme_list += tokens
        except UnicodeDecodeError:
            pass

    return morpheme_list


def generate_analytics(strings, knowfile=''):
    '''Returns analytics given list of strings to analyze and optionally the
    path to a file containing known morphemes to factor in to the analysis.
    Known morphemes will be left out of the frequency list, and used to tell
    the user their current comprehension and how many unknown morphemes must
    be learned to reach the comprehension cutoffs.
    '''
    # TODO: this function is disgusting

    # Get known morphemes if provided, otherwise none known
    known_morphemes = []
    if knowfile:
        print('Parsing known morphemes...')
        f = open(knowfile, 'r', encoding='utf-8')
        known_morphemes = get_morpheme_list(f.readlines())
        # Remove duplicates
        known_morphemes = list(dict.fromkeys(known_morphemes))

    # First generate frequency list and count morphemes.
    print('Generating frequency list...')
    input_morphemes = get_morpheme_list(strings)
    freq_dict = dict()
    total_morphs = 0
    total_known_morphs = 0

    for string in input_morphemes:
        # Exclude unhelpful single-non-CJK-character morphemes and known
        # morphemes in the frequency list, and count total morphemes and total
        # known morphemes ('total' as in including repeats)
        not_known = string not in known_morphemes
        valid = len(string) > 1 or len(string) == 1 and is_cjk(string)
        if valid:
            total_morphs += 1
            if not_known:
                if string in freq_dict:
                    freq_dict[string] += 1
                else:
                    freq_dict[string] = 1
            else:
                total_known_morphs += 1

    freq_list = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)

    # Now generate cutoff dictionary using frequency list/morpheme count info
    # using accumulator of how many total morphemes in the text are covered,
    # first by known morphemes and then by factoring in the most frequent
    # unknown morphemes
    print('Determining comprehension cutoffs...')
    # -1 = unset
    cutoff_dict = {80: -1, 85: -1, 90: -1, 95: -1, 98: -1, 99: -1}
    accumulator = total_known_morphs
    # Must first check if known morphemes already reach cutoff(s)
    for key in cutoff_dict:
        if key <= accumulator/total_morphs * 100:
            cutoff_dict[key] = 0
    # Now set the cutoffs that require more knowledge
    for i, morph in enumerate(freq_list, start=1):
        accumulator += morph[1]
        # !TODO: optimize this to only check lowest unset dict entry each loop
        for key in cutoff_dict:
            if (cutoff_dict[key] == -1 and
                    key <= accumulator/total_morphs * 100):
                cutoff_dict[key] = i

    # Finally get number of unique unknown morphemes
    unique_unknown_morphs = len(freq_dict)

    return Analytics(freq_list, cutoff_dict, total_morphs, total_known_morphs,
                     unique_unknown_morphs)
