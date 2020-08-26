'''
jstats - generate stats about Japanese text

Planned features:
- Epub file support
- Store user knowledge permanently
'''

import os.path
import sys
import argparse
from urllib.parse import urlparse

import analyze

import ebooklib
from ebooklib import epub


def options_prompt(text, valid_inputs, blank_default=''):
    '''Prompt user for input, giving options, and return it.
    Prompt will repeat until input is one of valid_inputs.
    Blank input will be treated as blank_default if provided.
    '''
    first = True
    for option in valid_inputs:
        if first:
            prompt_inputs = valid_inputs[0]
            first = False
        else:
            prompt_inputs += '/' + option

    prompt = text + ' (' + prompt_inputs
    if blank_default != '':
        prompt += ', default ' + blank_default
    prompt += '): '

    while True:
        i = input(prompt)
        if i in valid_inputs:
            break
        if i == '' and blank_default != '':
            return blank_default

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
    group_input = parser.add_mutually_exclusive_group()

    group_input.add_argument('-u', '--url',
                             help='specify a web URL for analysis')
    group_input.add_argument('-i', '--infile',
                             help=('specify an input file for analysis'
                                   ' (.html, .epub, .txt)'))
    parser.add_argument('-o', '--outfile',
                        help=('specify output file'
                              ' (stats.txt if no argument given)'),
                        nargs='?', const='stats.txt')
    parser.add_argument('-k', '--knowfile',
                        help=('specify an input file containing'
                              ' morphemes you know (.html, .epub, .txt)'))

    return parser


def interactive_set_args(args):
    '''Sets args interactively, as if they were specified on CLI.'''
    i = options_prompt('Analyze a webpage or a file?', ['w', 'f'], 'w')
    if i == 'w':
        args.url = noblank_prompt('Enter URL: ')
    elif i == 'f':
        args.infile = noblank_prompt('Enter filename: ')

    i = options_prompt('Input a knowledge file?', ['y', 'n'], 'n')
    if i == 'y':
        args.knowfile = noblank_prompt('Enter filename: ')

    i = options_prompt('Output to file?', ['y', 'n'], 'n')
    if i == 'y':
        args.outfile = input('Enter filename (blank for stats.txt): ')
        if not args.outfile:
            args.outfile = 'stats.txt'


def get_url_analytics(args):
    '''Returns analytics given args specifying a URL.'''
    # If invalid url, see if prepending http:// works; otherwise quit
    if not valid_url(args.url):
        args.url = 'http://' + args.url
    if not valid_url(args.url):
        print('An invalid URL was given.')
        sys.exit(1)

    html = analyze.load_page(args.url)
    soup = analyze.get_soup(html)

    return analyze.generate_analytics(soup.stripped_strings, args.knowfile)


def epub_to_html(epub_file):
    '''Converts epub to a single html file whose body contains the entire text
    of the novel. Returns the result.'''
    # First get individual soups of each html file
    html_files = []
    book = epub.read_epub(epub_file)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            html_files += [analyze.get_soup(item.get_content())]

    # Then append the bodies of each file to the first file, capturing all
    # the text we care about in one file
    if len(html_files) == 0:
        raise Exception('Failed to find html in epub')
    else:
        html = html_files[0]
        first = True
        for f in html_files:
            if first:
                first = False
            else:
                for element in f.body:
                    html.body.append(element)

    return html


def get_infile_analytics(args):
    '''Returns analytics given args specifying an infile.'''
    infile_extension = os.path.splitext(args.infile)[1]

    if infile_extension in {'.html', '.htm', '.epub'}:
        if infile_extension == '.epub':
            html = epub_to_html(args.infile)
        else:
            html = open(args.infile, 'r', encoding='utf-8')

        soup = analyze.get_soup(html)
        return analyze.generate_analytics(soup.stripped_strings, args.knowfile)

    if infile_extension in {'.txt', ''}:
        if infile_extension == '':
            prompt = 'Given input filename has no extension. Treat as .txt?'
            i = options_prompt(prompt, ['y', 'n'], 'y')
            if i == 'n':
                print('Quitting.')
                sys.exit(1)

        txt = open(args.infile, 'r', encoding='utf-8')

        return analyze.generate_analytics(txt.readlines(), args.knowfile)

    print('Invalid file extension.')
    sys.exit(1)


def output_analytics(analytics, file_name=''):
    '''Outputs analytics object to given filename, or to stdout if none given.
    If the provided analytics object has no morphemes, instead just prints
    that no morphemes were found.
    '''
    # ! TODO: optimize by moving the if statements outside of the for loops
    if analytics.total_morphs > 0:
        using_output_file = file_name != ''
        if using_output_file:
            print('Writing results to ' + file_name + '...')
            f = open(file_name, 'w', encoding='utf-8')

        comprehension = analytics.total_known_morphs / analytics.total_morphs
        # 0 comprehension means user hasn't input a knowledge file
        if comprehension != 0:
            comprehension_str = str(round(comprehension * 100))
            output_line1 = ('Your current comprehension is '
                            + comprehension_str + '%.')
            output_line2 = ('(You know ' + str(analytics.total_known_morphs)
                            + ' of ' + str(analytics.total_morphs)
                            + ' morphemes.)')

            if using_output_file:
                f.write(output_line1 + '\n')
                f.write(output_line2 + '\n')
            else:
                print(output_line1)
                print(output_line2)

        for key in analytics.cutoff_dict:
            output_line = (str(key)
                           + ('% comprehension is gained after unknown unique '
                           'morpheme ')
                           + str(analytics.cutoff_dict[key]) + ' of '
                           + str(analytics.unique_unknown_morphs))
            if using_output_file:
                f.write(output_line + '\n')
            else:
                print(output_line)

        for i, morph in enumerate(analytics.freq_list, start=1):
            output_line = (str(i) + ': ' + str(morph[0]) + ' ' + str(morph[1]))
            if using_output_file:
                f.write(output_line + '\n')
            else:
                print(output_line)

        if using_output_file:
            f.close()
    else:
        print('No valid Japanese morphemes found.')


def main():
    '''Main function.'''
    os.environ['MECAB_CHARSET'] = 'utf-8'

    parser = get_parser()
    args = parser.parse_args()

    interactive = False
    if len(sys.argv) <= 1:
        interactive = True
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
    else:
        raise Exception('No arguments set for analysis')

    if args.outfile:
        output_analytics(analytics, args.outfile)
    else:
        output_analytics(analytics)

    if interactive:
        input('Press enter to exit.')


if __name__ == '__main__':
    '''
    Catch and display all top-level exceptions, preventing crashes that
    make output unreadable in interactive mode on Windows.
    '''
    try:
        main()
    except SystemExit:  # Don't print exit info when user runs -h
        pass
    except BaseException:  # pylint: disable=broad-except
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
        input('Press enter to exit.')
