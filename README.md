# jstats

jstats is a python script intended to help Japanese learners easily analyze and gather basic statistics about Japanese text. Currently, it can analyze text files, html files, and webpages. It outputs a frequency list generated from the text as well as some numbers regarding how many morphemes would need to be known to reach a certain level of comprehension.

# Dependencies

jstats uses `requests` for fetching URLs, `beautifulsoup4` for ease of parsing HTML, and `natto-py` for extracting morphemes from Japanese text.  These can be installed with pip:
```
pip install requests
pip install beautifulsoup4
pip install natto-py
```
natto-py requires that the `mecab` (and `mecab-config` on Linux/Mac) executables are in your `PATH`. See the [natto-py repo](https://github.com/buruzaemon/natto-py) for more information. Windows users may find it necessary to set the environment variable `MECAB_CHARSET=utf-8` if mecab complains about shift-jis encoding.

# Usage
For CLI:
```
usage: jstats.py [-h] [-u URL | -i INFILE] [-o OUTFILE]

jstats - generate stats about Japanese text

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     specify a web URL for analysis
  -i INFILE, --infile INFILE
                        specify an input file for analysis (.html or .txt)
  -o OUTFILE, --outfile OUTFILE
                        specify output file (defaults to stats.txt)
```
Or just run the script directly for interactive mode.

# Notes

The script ignores morphemes such as particles (は, が, よ, etc) or exclamatory sounds (あ, う) in order to focus on vocabulary. However, morphemes such as 〜られる will be listed, even though they are not quite words.
