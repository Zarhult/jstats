# jstats

`jstats` is a python script intended to help Japanese learners easily analyze and gather basic statistics about Japanese text. Currently, it can analyze text files, html files, and webpages. It outputs a frequency list generated from the text as well as some numbers regarding how many morphemes would need to be known to reach a certain level of comprehension.

# Installation

`jstats`, since it uses `natto-py`, relies on mecab for picking out morphemes from Japanese text. So first, mecab must be installed. On Windows it can simply be installed from [this webpage](https://taku910.github.io/mecab/). Be sure to specify utf-8 as the encoding during the installation, or `jstats` may not work. Linux users, on the other hand, can likely just install mecab with their package manager. For example, on Ubuntu, `sudo apt install libmecab-dev` will suffice. 

Afterward, things may "just work" after grabbing the latest release and running the executable. But if problems happen with mecab, see the [natto-py repo](https://github.com/buruzaemon/natto-py) for more info on the mecab dependency. If trouble persists, feel free to open an issue, as this project is still new and potentially buggy. Note that there is currently no Mac release, but Mac users can run `jstats.py` directly by installing python and the below dependencies.

Currently, the Linux release must be run from an existing terminal, i.e. `./jstats` or `./jstats -u http://github.com/Zarhult/jstats`.

# Python Dependencies

`jstats` uses `requests` for fetching URLs, `beautifulsoup4` for ease of parsing HTML, and `natto-py` for extracting morphemes from Japanese text.  These can be installed with pip:
```
pip install requests
pip install beautifulsoup4
pip install natto-py
```
This only matters if you want to run `jstats.py` with your own installation of python. As stated above, it is also necessary to install mecab.

# Usage

For CLI, see `jstats -h`.
For interactive mode, simply run the executable directly.

# Notes

The script ignores morphemes such as particles (は, が, よ, etc) or exclamatory sounds (あ, う) in order to focus on vocabulary. However, morphemes such as 〜られる will be listed, even though they are not quite words.
