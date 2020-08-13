'''
jstats - generate stats about Japanese text
'''

import os.path
import sys
import argparse
from urllib.parse import urlparse

import analyze


def options_prompt(text, valid_inputs):
    '''Prompt user for input and return it.
    Prompt will repeat until input is one of valid_inputs.
    '''
    while True:
        i = input(text)
        if i in valid_inputs:
            break

    return i


def noblank_prompt(text):
    '''Prompt user for input and return it.
    Prompt will repeat if input is empty.
    '''
    while True:
        i = input(text)
        if i != '':
            break

    return i


def valid_url(url):
    '''Returns whether or not given url string is a valid url.'''
    if url != '':
        validate = urlparse(url)
        if validate.scheme == '' or validate.netloc == '':
            return False
        return True

    return False


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
                        help='specify output file (defaults to stats.txt)',
                        default='stats.txt')

    return parser


def interactive_set_args(args):
    '''Sets args interactively, as if they were specified on CLI.'''
    i = options_prompt('Custom output filename? (y/n): ', ['y', 'n'])
    if i == 'y':
        args.outfile = noblank_prompt('Enter filename: ')

    i = options_prompt('Analyze a webpage or a file? (w/f): ', ['w', 'f'])
    if i == 'w':
        args.url = noblank_prompt('Enter URL: ')
    elif i == 'f':
        args.infile = noblank_prompt('Enter filename: ')


def get_url_analytics(args):
    '''Return analytics given args specifying a URL.'''
    # If invalid url, see if appending http:// works; otherwise quit
    if not valid_url(args.url):
        args.url = 'http://' + args.url
    if not valid_url(args.url):
        print('An invalid URL was given.')
        sys.exit(1)

    html = analyze.load_page(args.url)
    soup = analyze.get_soup(html)
    return analyze.generate_analytics(soup.stripped_strings)


def get_infile_analytics(args):
    '''Return analytics given args specifying an infile.'''
    infile_extension = os.path.splitext(args.infile)[1]

    if infile_extension in {'.html', '.htm'}:
        try:
            html = open(args.infile, 'r')
        except FileNotFoundError:
            print('File not found!')
            sys.exit(1)

        soup = analyze.get_soup(html)
        return analyze.generate_analytics(soup.stripped_strings)

    if infile_extension in {'.txt', ''}:
        if infile_extension == '':
            i = options_prompt(('Given filename has no extension. '
                                + 'Proceed anyways? (y/n): '), ['y', 'n'])
            if i == 'n':
                print('Quitting.')
                sys.exit(1)

        try:
            txt = open(args.infile, 'r')
        except FileNotFoundError:
            print('File not found!')
            sys.exit(1)

        return analyze.generate_analytics(txt.readlines())

    print('Invalid file extension.')
    sys.exit(1)


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


def main():
    '''Main function.'''
    parser = get_parser()
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        interactive_set_args(args)

    '''
    Args have now been set up either interactively or by CLI.
    All input validation should happen AFTER this point, for
    equal results between CLI and interactive mode.
    '''

    if args.url:
        analytics = get_url_analytics(args)
    elif args.infile:
        analytics = get_infile_analytics(args)

    output_analytics(analytics, args.outfile)


if __name__ == '__main__':
    main()
