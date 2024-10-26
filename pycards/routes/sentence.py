from dataclasses import dataclass
from pathlib import Path
from flask import Blueprint, request, redirect, url_for, render_template

from pycards.mdict_query.mdict_utils import MDXDict
from ..models import get_db_connection
from ..language.english import english_nlp, getLemma

sentence_bp = Blueprint("sentence", __name__, url_prefix="/sentence")
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


@sentence_bp.route("/manage")
def manage_sentences():
    with get_db_connection() as conn:
        sentences = conn.execute(
            "SELECT id,content,descriptions FROM sentences order by id desc"
        ).fetchall()
        conn.close()
        sentences = [
            DBSentence(sentence_id=row[0], content=row[1], descriptions=row[2])
            for row in sentences
        ]
        return render_template("manage_sentences.html", sentences=sentences)


@sentence_bp.route("/delete/<int:sentence_id>")
def delete_sentence(sentence_id):
    with get_db_connection() as db:
        db.execute("DELETE FROM sentences WHERE id = ?", (sentence_id,))
        db.commit()
        return redirect(url_for("sentence.manage_sentences"))
