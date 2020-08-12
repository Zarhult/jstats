import sys
import requests
from bs4 import BeautifulSoup
from natto import MeCab

class Analytics:
    '''
    The Analytics class contains all the data gathered and organized
    from a webpage.

    Attributes:
        freq_list: sorted list of tuples of morpheme/its frequency
        total_morphs: total number of morphemes, including duplicates
        unique_morphs: total number of unique morphemes
        cutoff_dict: a dictionary mapping desired percent comprehension
                        to necessary number of (most common) unique 
                        morphemes known
    '''
    def __init__(self, freq_list, total_morphs, unique_morphs, cutoff_dict):
        self.freq_list = freq_list
        self.total_morphs = total_morphs
        self.unique_morphs = unique_morphs
        self.cutoff_dict = cutoff_dict

def is_cjk(char):
    ''' Returns whether or not char is a CJK character. '''
    if '\u4E00' <= char <= '\u9FFF':
        return True
    else:
        return False

def load_page(URL):
    ''' Returns parsed soup object given a URL. '''
    print('Fetching HTML...')
    page = requests.get(URL)

    print('Parsing HTML...')
    soup = BeautifulSoup(page.content, 'html.parser')

    print('Removing furigana...')
    for rt in soup.select('rt'):
        rt.extract()

    return soup

def generate_analytics(soup):
    ''' Returns analytics given soup. '''
    # Make MeCab output nothing but morphemes
    fmt = { 'node_format': r'%m\n',
            'bos_format': r'',
            'eos_format': r'',
            'unk_format': r''        }

    nm = MeCab(options=fmt)

    # First generate frequency list and count morphemes.
    print('Generating frequency list...')
    freq_dict = dict()
    total_morphs = 0
    for string in soup.stripped_strings:
        tokens = nm.parse(string)
        tokens = tokens.splitlines()
        for string in tokens:
            # Exclude unhelpful single-non-CJK-character morphemes
            if len(string) == 1 and is_cjk(string) or len(string) > 1:
                if string in freq_dict:
                    freq_dict[string] += 1
                else:
                    freq_dict[string] = 1
                total_morphs += 1

    freq_list = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)

    # Now generate cutoff dictionary using frequency list info
    print('Determining comprehension cutoffs...')
    cutoff_dict = { 80: 0, 85: 0, 90: 0, 95: 0, 98: 0, 99: 0 }
    accumulator = 0
    for i, morph in enumerate(freq_list, start = 1):
        accumulator += morph[1]
        # !!Should optimize this to only check lowest unset dict entry each loop
        for key in cutoff_dict:
            if (cutoff_dict[key] == 0 
                and key <= accumulator/total_morphs * 100):
                cutoff_dict[key] = i

    # Finally get number of unique morphemes
    unique_morphs = len(freq_dict)

    return Analytics(freq_list, total_morphs, unique_morphs, cutoff_dict)

def output_analytics(analytics, file_name = ''):
    ''' 
    Outputs analytics object to given filename, or to stdout if none given.
    '''
    f = ''
    if file_name is not '':
        print('Writing results to ' + file_name + '...')
        f = open(file_name, 'w')

    for key in analytics.cutoff_dict:
        output_line = (str(key) + '% comprehension is at unique morpheme ' +
                       str(analytics.cutoff_dict[key]) + ' of ' + 
                       str(analytics.unique_morphs))
        if file_name is not '':
            f.write(output_line + '\n')
        else:
            print(output_line)

    for i, morph in enumerate(analytics.freq_list, start = 1):
        output_line = (str(i) + ': ' + str(morph[0]) + ' ' + str(morph[1]))
        if file_name is not '':
            f.write(output_line + '\n')
        else:
            print(output_line)
    
    if file_name is not '':
        f.close()

if __name__ == '__main__':
    '''
    Outputs analytics for a webpage to a file. 

    If no commandline arguments given, prompts user for a URL, then writes 
        results to jstats.txt. 
    If there is one argument, that argument will be used as the URL and no 
        prompt will be needed. 
    If there are two arguments, the second argument will be used as the output 
        file name rather than the default jstats.txt.
    '''
    URL = ''
    output_filename = 'jstats.txt'
    arg_num = len(sys.argv)

    if arg_num == 1:
        URL = input('Enter URL: ')
    elif arg_num in {2, 3}:
        URL = str(sys.argv[1])
        if arg_num == 3:
            output_filename = str(sys.argv[2])
    else:
        raise RuntimeError('Too many commandline arguments')

    soup = load_page(URL)
    analytics = generate_analytics(soup)
    output_analytics(analytics, output_filename)

