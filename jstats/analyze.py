'''
Module containing functions for generating analytics.
'''

import os
import shelve

import requests
from bs4 import BeautifulSoup
from natto import MeCab


class Analytics:
    '''
    The Analytics class contains all the data gathered and organized
    from the inputs.

    Attributes:
        freq_list: sorted list of tuples of unknown morpheme/its frequency
        cutoff_dict: a dictionary mapping desired percent comprehension
                     to necessary number of (most common) unique
                     unknown morphemes learned
        total_morphs: total number of morphemes, including duplicates
        total_known_morphs: total number of known morphemes, including
                            duplicates
        unique_unknown_morphs: total number of unique unknown morphemes
    '''
    def __init__(self, input_morphemes, known_morphemes):
        self.make_freq_list(input_morphemes, known_morphemes)
        self.calc_cutoff_dict()

    def make_freq_list(self, input_morphemes, known_morphemes):
        '''Generates frequency list given list of morphemes to generate
        it from, and a list of the user's known morphemes. Excludes
        single-non-CJK-character morphemes and known morphemes from
        the list. Also sets total_morphs, total_known_morphs, and
        unique_unknown_morphs using frequency info.'''
        print('Generating frequency list...')
        freq_dict = dict()
        self.total_morphs = 0
        self.total_known_morphs = 0
        self.unique_unknown_morphs = 0

        for string in input_morphemes:
            not_known = string not in known_morphemes
            valid = len(string) > 1 or len(string) == 1 and is_cjk(string)
            if valid:
                self.total_morphs += 1
                if not_known:
                    if string in freq_dict:
                        freq_dict[string] += 1
                    else:
                        freq_dict[string] = 1
                else:
                    self.total_known_morphs += 1

        self.unique_unknown_morphs = len(freq_dict)
        self.freq_list = sorted(freq_dict.items(), key=lambda x: x[1],
                                reverse=True)


    def calc_cutoff_dict(self):
        '''Generates cutoff dictionary using existing frequency list/morpheme
        count info. Uses accumulator of how many total morphemes in the text
        are covered, first by known morphemes and then by factoring in the most
        frequent unknown morphemes.'''
        print('Determining comprehension cutoffs...')
        # -1 = unset
        self.cutoff_dict = {80: -1, 85: -1, 90: -1, 95: -1, 98: -1, 99: -1}

        accumulator = self.total_known_morphs
        # Must first check if known morphemes already reach cutoff(s)
        for key in self.cutoff_dict:
            if key <= accumulator/self.total_morphs * 100:
                self.cutoff_dict[key] = 0
        # Now set the cutoffs that require more knowledge
        for i, morph in enumerate(self.freq_list, start=1):
            accumulator += morph[1]
            for key in self.cutoff_dict:
                if (self.cutoff_dict[key] == -1 and
                        key <= accumulator/self.total_morphs * 100):
                    self.cutoff_dict[key] = i

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


def get_file_morphemes(filename):
    '''Returns the morphemes found from given filename.'''
    file = open(filename, 'r', encoding='utf-8')
    known_morphemes = get_morpheme_list(file.readlines())
    # Remove duplicates
    known_morphemes = list(dict.fromkeys(known_morphemes))

    return known_morphemes


def make_knowledge_file(known_morphemes, knowledge_file):
    '''Given a list of known morphemes, stores user knowledge in
    knowledge_file, unless it already exists.'''
    if not os.path.isfile(knowledge_file):
        print('Creating knowledge data file...')
        data = shelve.open(knowledge_file)
        data['k'] = known_morphemes
        data.close()


def get_known_morphemes(knowfile=''):
    '''Returns user's known unique morphemes. First tries to read them from
    an existing file called "knowledge". If it does not exist, and a knowfile
    argument is provided, creates "knowledge" from that file's contents before
    returning them. Otherwise return empty list (no knowledge).'''
    script_dir = os.path.dirname(os.path.realpath(__file__))
    knowledge_file = script_dir + '/knowledge'
    if os.path.isfile(knowledge_file):
        print('Found and using "knowledge" file.')
        data = shelve.open(knowledge_file)
        known_morphemes = data['k']
        data.close()
    elif knowfile:
        print('Parsing known morphemes...')
        known_morphemes = get_file_morphemes(knowfile)
        make_knowledge_file(known_morphemes, knowledge_file)
    else:
        known_morphemes = []

    return known_morphemes


def generate_analytics(strings, knowfile=''):
    '''Returns analytics given list of strings to analyze and optionally the
    path to a file containing known morphemes to factor in to the analysis.
    Known morphemes will be left out of the frequency list, and used to tell
    the user their current comprehension and how many unknown morphemes must
    be learned to reach the comprehension cutoffs.
    '''
    input_morphemes = get_morpheme_list(strings)
    known_morphemes = get_known_morphemes(knowfile)

    return Analytics(input_morphemes, known_morphemes)
