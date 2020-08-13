'''
Module containing functions for generating analytics.
'''

import sys
from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from natto import MeCab


Analytics = namedtuple('Analytics', [
    'freq_list',
    'cutoff_dict',
    'total_morphs',
    'unique_morphs',
])
Analytics.__doc__ = '''\
    The Analytics object contains all the data gathered and organized
    from whatever source.

    Attributes:
        freq_list: sorted list of tuples of morpheme/its frequency
        cutoff_dict: a dictionary mapping desired percent comprehension
                     to necessary number of (most common) unique
                     morphemes known
        total_morphs: total number of morphemes, including duplicates
        unique_morphs: total number of unique morphemes'''


def is_cjk(char):
    '''Returns whether or not char is a CJK character.'''
    if '\u4E00' <= char <= '\u9FFF':
        return True

    return False


def load_page(url):
    '''Returns html given a URL.'''
    try:
        print('Fetching HTML...')
        page = requests.get(url, timeout=1)
        return page.content
    except requests.exceptions.RequestException:
        print('Failed to connect to ' + url)
        sys.exit(1)


def get_soup(html):
    '''Returns parsed soup object given html.'''
    print('Parsing html...')
    soup = BeautifulSoup(html, 'html.parser')

    print('Removing furigana...')
    for rt_tag in soup.select('rt'):
        rt_tag.extract()

    return soup


def generate_analytics(strings):
    '''Returns analytics given list of strings.'''
    # Make MeCab output nothing but morphemes
    fmt = {'node_format': r'%m\n',
           'bos_format': r'',
           'eos_format': r'',
           'unk_format': r''}

    mecab = MeCab(options=fmt)

    # First generate frequency list and count morphemes.
    print('Generating frequency list...')
    freq_dict = dict()
    total_morphs = 0
    for line in strings:
        tokens = mecab.parse(line)
        tokens = tokens.splitlines()
        for string in tokens:
            # Exclude unhelpful single-non-CJK-character morphemes
            if len(string) > 1 or len(string) == 1 and is_cjk(string):
                if string in freq_dict:
                    freq_dict[string] += 1
                else:
                    freq_dict[string] = 1
                total_morphs += 1

    freq_list = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)

    # Now generate cutoff dictionary using frequency list info
    print('Determining comprehension cutoffs...')
    cutoff_dict = {80: 0, 85: 0, 90: 0, 95: 0, 98: 0, 99: 0}
    accumulator = 0
    for i, morph in enumerate(freq_list, start=1):
        accumulator += morph[1]
        # !Should optimize this to only check lowest unset dict entry each loop
        for key in cutoff_dict:
            if (cutoff_dict[key] == 0 and
                    key <= accumulator/total_morphs * 100):
                cutoff_dict[key] = i

    # Finally get number of unique morphemes
    unique_morphs = len(freq_dict)

    return Analytics(freq_list, cutoff_dict, total_morphs, unique_morphs)
