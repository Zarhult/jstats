# jstats

jstats is a python script intended to help Japanese learners easily analyze and gather basic statistics about webpages with Japanese text. Currently, it outputs a text file containing a frequency list and information about how many morphemes must be known to reach a certain level of comprehension.

# Dependencies

jstats uses Beautiful Soup 4 for ease of parsing HTML and natto-py for extracting morphemes from Japanese text.  They can be installed with pip:
```
pip install beautifulsoup4
pip install natto-py
```
natto-py requires that the `mecab` (and `mecab-config` on Linux/Mac) executables are in your `PATH`. See the [natto-py repo](https://github.com/buruzaemon/natto-py) for more information.

# Usage

Simply run the script like any other python script, optionally with arguments to specify the desired URL immediately (skipping the prompt), or a custom output file name. The default output file is jstats.txt.
```
python jstats.py [URL] [FILENAME]
```

# Notes

The script ignores morphemes such as particles (は, が, よ, etc) or exclamatory sounds (あ, う) in order to focus on vocabulary. However, morphemes such as 〜られる will be listed, even though they are not quite words.
