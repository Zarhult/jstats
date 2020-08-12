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

```
usage: jstats.py [-h] (-u URL | -i INFILE) [-o OUTFILE]

jstats - generate stats about Japanese text

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     specify a web URL for analysis
  -i INFILE, --infile INFILE
                        specify an input file for analysis (.html or .txt)
  -o OUTFILE, --outfile OUTFILE
                        specify output file (defaults to stats.txt)

```

# Notes

The script ignores morphemes such as particles (は, が, よ, etc) or exclamatory sounds (あ, う) in order to focus on vocabulary. However, morphemes such as 〜られる will be listed, even though they are not quite words.
