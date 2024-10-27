# Anki card creation tool

This is a simple tool designed to create Anki cards easily, particularly for English and Japanese(Not avaiable yet) sentences. It utilizes Spacy for English tokenization and lemmatization, making it easier to look up words in a dictionary. Additionally, it uses Mdict as dictionary.

## How to use
### Ensure uv installed
https://github.com/astral-sh/uv

## Install dependencies
```bash
# sync dependencies
uv sync
# install spacy model
uv run pre-install.py
# run http server
uv run run.py
```

## export csv
`uv run export.py`
