# jstats

jstats is a python script intended to help users easily analyze and gather basic statistics about webpages with Japanese text. It currently simply outputs a morpheme frequency list, but more analytics are planned.

# Dependencies

jstats uses Beautiful Soup 4 for ease of parsing HTML and natto-py for extracting morphemes from Japanese text.  They can be installed with pip:
```
pip install beautifulsoup4
pip install natto-py
```
natto-py requires that the `mecab` (and `mecab-config` on Linux/Mac) executables are in your `PATH`. See [the natto-py repo](https://github.com/buruzaemon/natto-py) for more information.

# Usage

Simply pass a URL to the script as in
```
python jstats.py [URL]
```
or just run the script with
```
python jstats.py
````
and enter a URL at the prompt.

# Notes

In building the frequency list, the script ignores morphemes such as particles (は, が, の) since they fall more in the realm of grammar than vocabulary. Similarly exclamatory sounds such as あ are ignored.
