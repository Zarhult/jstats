# jstats

`jstats` is a python program intended to help Japanese learners easily analyze and gather basic statistics about Japanese text. Features include:
* Works on websites, ebooks (.epub), html files, and text files
* Generates frequency lists (only of morphemes unknown to the user, if desired)
* Determines how many of the most frequent morphemes must be known for a certain level of comprehension
* Import text file containing known morphemes, to personalize results

For instance, suppose you are an intermediate learner and you want to read a Japanese ebook. Assuming you use Anki, you could export your deck as a .txt file, then feed that and the epub file to `jstats`. The result would be a text file telling you what your current percent comprehension is, what the most common unknown morphemes are, and how many of them you need to learn to reach, say, 90% comprehension. This will give you an idea of how hard the book will be for you, and a list of the most important words/morphemes to learn to quickly bring up your comprehension of the ebook you're interested in.

## Example output from コンビニ人間 (shortened)
```
Your current comprehension is 82%.
(You know 17541 of 21493 morphemes.)
80% comprehension is gained after unknown unique morpheme 0 of 1972
85% comprehension is gained after unknown unique morpheme 30 of 1972
90% comprehension is gained after unknown unique morpheme 259 of 1972
95% comprehension is gained after unknown unique morpheme 898 of 1972
98% comprehension is gained after unknown unique morpheme 1543 of 1972
99% comprehension is gained after unknown unique morpheme 1758 of 1972
1: 白羽 254
2: 店員 56
3: 菅原 43
4: 喋り 24
5: ドア 23
6: 夜勤 20
7: いらっしゃい 19
8: 働いて 19
9: ようだった 18
10: のだった 18
11: 縄文 18
12: 旦那 17
...
```
In the above example, the most common word the user does not know is 白羽 (a name), which occurs 254 times. Second is 店員, which occurs 56 times. If the user wanted to reach 90% comprehension before reading the book, they would need to learn the top 259 words/morphemes in the example. Be warned that although 90% might sound good, it actually means you are missing every 10th word on average.

# Installation

`jstats`, since it uses `natto-py`, relies on mecab for picking out morphemes from Japanese text. So first, mecab must be installed. On Windows it can simply be installed from [this webpage](https://taku910.github.io/mecab/). Be sure to specify utf-8 as the encoding during the installation, or `jstats` may not work. Linux users, on the other hand, can likely just install mecab with their package manager. For example, on Debian or Ubuntu, `sudo apt install mecab libmecab-dev` will suffice. 

Afterward, things may "just work" after grabbing the latest release and running the executable. But if problems happen with mecab, see the [natto-py repo](https://github.com/buruzaemon/natto-py) for more info on the mecab dependency. If trouble persists, feel free to open an issue, as this project is still new and potentially buggy. Note that there is currently no Mac release, but Mac users can run `jstats.py` directly by installing python and the below dependencies.

Currently, the Linux release must be run from an existing terminal, i.e. `./jstats` or `./jstats -u http://github.com/Zarhult/jstats`.

# Python Dependencies

`jstats` uses `requests` for fetching URLs, `beautifulsoup4` for ease of parsing HTML, `natto-py` for extracting morphemes from Japanese text, and `ebooklib` for working with ebook files.  These can be installed with pip:
```
pip install requests
pip install beautifulsoup4
pip install natto-py
pip install ebooklib
```
This only matters if you want to run `jstats.py` with your own installation of python. As stated above, it is also necessary to install mecab.

# Usage

For CLI, see `jstats -h`.
For interactive mode, simply run the executable directly.

Note that if you use monolingual definitions in your Anki collection, exporting your deck as a .txt and giving that to jstats will cause jstats to assume you know every single word in your monolingual definitions, which you probably don't. There is an easy solution to this. First, create a new empty deck in Anki. Then, export your Japanese deck as a .txt, and then import that .txt back into Anki. In the prompt you can specify that you want to import it into the new deck you just created, and have it ignore the monolingual definition field. As a result you will have a duplicate of your Japanese deck with all the definitions removed. Finally you can just export that deck as a .txt and give it to jstats. You can also go ahead and delete the duplicate deck after you successfuly export it as a .txt.

# Notes

The program ignores morphemes such as particles (は, が, よ, etc) or exclamatory sounds (あ, う) in order to focus on vocabulary. However, morphemes such as 〜られる will be listed, even though they are not quite words.
