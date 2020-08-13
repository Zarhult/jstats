'''
jstats - generate stats about Japanese text
'''

import os.path
import sys
import argparse
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
    print('Fetching HTML...')
    page = requests.get(url, timeout=1)

    return page.content


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


def output_analytics(analytics, file_name=''):
    '''Outputs analytics object to given filename, or to stdout if none given.
    If the provided analytics object has no morphemes, instead just prints
    that no morphemes were found.
    '''
    if analytics.total_morphs > 0:
        if file_name != '':
            print('Writing results to ' + file_name + '...')
            file = open(file_name, 'w')

        for key in analytics.cutoff_dict:
            output_line = (str(key) + '% comprehension is at unique morpheme '
                           + str(analytics.cutoff_dict[key]) + ' of '
                           + str(analytics.unique_morphs))
            if file_name != '':
                file.write(output_line + '\n')
            else:
                print(output_line)

        for i, morph in enumerate(analytics.freq_list, start=1):
            output_line = (str(i) + ': ' + str(morph[0]) + ' ' + str(morph[1]))
            if file_name != '':
                file.write(output_line + '\n')
            else:
                print(output_line)

        if file_name != '':
            file.close()
    else:
        print('No valid Japanese morphemes found.')


def get_parser():
    '''Setup argparse.'''
    description = 'jstats - generate stats about Japanese text'
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-u', '--url',
                       help='specify a web URL for analysis')
    group.add_argument('-i', '--infile',
                       help='specify an input file for analysis \
                       (.html or .txt)')
    parser.add_argument('-o', '--outfile',
                        help='specify output file (defaults to stats.txt)')

    return parser


def interactive_set_args(args):
    '''Sets args interactively, as if they were specified on CLI.'''
    prompt = 'Analyze a webpage or a file? (w/f): '
    while True:
        i = input(prompt)
        if i == 'w':
            args.url = input('Enter URL: ')
            break
        if i == 'f':
            args.infile = input('Enter file path: ')
            break
    prompt = 'Custom output filename? (y/n): '
    while True:
        i = input(prompt)
        if i == 'y':
            args.outfile = input('Enter filename: ')
            break
        if i == 'n':
            break


def main():
    '''Main function.'''
    parser = get_parser()
    args = parser.parse_args()

    interactive = False
    if len(sys.argv) <= 1:
        interactive_set_args(args)
        interactive = True

    # Args have now been set up either interactively or by CLI
    outfile = 'stats.txt'
    if args.outfile:
        outfile = args.outfile

    if args.url:
        html = load_page(args.url)
        soup = get_soup(html)
        analytics = generate_analytics(soup.stripped_strings)
    elif args.infile:
        infile_extension = os.path.splitext(args.infile)[1]
        if infile_extension in {'.html', '.htm'}:
            html = open(args.infile, 'r')
            soup = get_soup(html)
            analytics = generate_analytics(soup.stripped_strings)
        elif infile_extension in {'.txt', ''}:
            if infile_extension == '':
                prompt = ('Assume extensionless input file is a text file? '
                          + '(y/n): ')
                while True:
                    i = input(prompt)
                    if i == 'y':
                        break
                    if i == 'n':
                        print('Quitting.')
                        sys.exit(1)

            txt = open(args.infile, 'r')
            analytics = generate_analytics(txt.readlines())
        else:
            parser.print_help()
            sys.exit(1)

    output_analytics(analytics, outfile)

    if interactive:
        input('Press enter to exit.')


if __name__ == '__main__':
    main()
