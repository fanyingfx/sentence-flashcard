from dataclasses import dataclass
from pathlib import Path
import spacy
from lemminflect import getLemma
from pycards.mdict_query.mdict_utils import MDXDict

__all__ = ["english_nlp", "parse_sentence"]

english_nlp = spacy.load("en_core_web_sm")

olad_10_dir = "/home/fan/Documents/dicts/Eng/olad10"

dict_name = "Oxford Advanced Learner's Dictionary 10th.mdx"

MDXPATH = Path(olad_10_dir) / dict_name

mdict = MDXDict(MDXPATH)


@dataclass
class Word:
    text: str
    lemma: str


@dataclass
class Sentence:
    _text: str
    sentence_id: int
    words: list[Word]
    descriptions: str


@dataclass
class DBSentence:
    sentence_id: int
    content: str
    descriptions: str


def parse_sentence(sentence):
    id = sentence[0]
    sentence_text = sentence[1]
    words = []
    for token in english_nlp(sentence_text):
        lemma = token.lemma_
        if token.pos_ == "NOUN" and token.lemma_.endswith("ing"):
            if not mdict.lookup(lemma):
                lemma = getLemma(token.text, "VERB")[0]
        words.append(Word(token.text, lemma))
    descriptions = sentence[2]
    return Sentence(sentence[1], id, words, descriptions)
