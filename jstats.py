import sys
import requests
from bs4 import BeautifulSoup
from natto import MeCab

fmt = { 'node_format': r'%m\n',
        'bos_format': r'',
        'eos_format': r'',
        'unk_format': r''        }

nm = MeCab(options=fmt)

# Morphemes to ignore in frequency list
excludes = ['　', '（', '）', '「', '」', '『', '』', '', '', '', '', '', '', '']

def load_page(URL):
    ''' Returns parsed soup object given a URL. '''
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Remove furigana
    while soup.rt != None:
        rt_tag = soup.rt
        rt_tag.decompose()
    return soup

def generate_freq_list(soup):
    ''' Returns sorted frequency list given soup. '''
    freq_dict = dict()
    for string in soup.stripped_strings:
        tokens = nm.parse(string)
        tokens = tokens.splitlines()
        for string in tokens:
            if string not in excludes:
                if string in freq_dict:
                    freq_dict[string] += 1
                else:
                    freq_dict[string] = 1

    freq_list = sorted(freq_dict.items(), key=lambda x: x[1])
    return freq_list

if __name__ == '__main__':
    URL = ''
    if len(sys.argv) == 1:
        URL = input('Enter URL: ')
    elif len(sys.argv) == 2:
        URL = str(sys.argv[1])
    else:
        raise RuntimeError("Invalid commandline arguments")

    soup = load_page(URL)
    freq = generate_freq_list(soup)
    for key in freq:
        print(key[0], key[1])
