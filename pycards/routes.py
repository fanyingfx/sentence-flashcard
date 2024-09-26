from dataclasses import dataclass
from flask import Blueprint, request, redirect, url_for, render_template
from .models import get_db_connection

from pathlib import Path
from .mdict_query.mdict_utils import MDXDict
from .language.english import english_nlp, getLemma

olad_10_dir = "/home/fan/Documents/dicts/Eng/olad10"
dict_name = "Oxford Advanced Learner's Dictionary 10th.mdx"

MDXPATH = Path(olad_10_dir) / dict_name

mdict = MDXDict(MDXPATH)
main_bp = Blueprint("main", __name__)


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
    # words = [Word(word, word) for word in sentence[1].split()]
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


def render_home(keep_descriptions=False):
    # db = get_db()
    with get_db_connection() as db:
        cur = db.execute(
            "SELECT id,content,descriptions FROM sentences order by id desc"
        )
        sentences = cur.fetchall()
        sentences = [parse_sentence(row) for row in sentences]
        return render_template("home.html", sentences=sentences)


@main_bp.route("/")
def home():
    # db = get_db()
    # cur = db.execute("SELECT id,content,descriptions FROM sentences")
    # sentences = cur.fetchall()
    # sentences = [parse_sentence(row) for row in sentences]
    # return render_template("home.html", sentences=sentences)
    return render_home()


@main_bp.route("/submit", methods=["POST"])
def submit():
    sentence = request.form["sentence"]
    descriptions = request.form["descriptions"]
    keep_descriptions = "keep_descriptions" in request.form

    if sentence:
        with get_db_connection() as db:
            db.execute(
                "INSERT INTO sentences (content,descriptions) VALUES (?,?)",
                [sentence, descriptions],
            )
            db.commit()
            if keep_descriptions:
                return render_home(keep_descriptions=True)
    return redirect(url_for("main.home"))


@main_bp.route("/submit_word", methods=["POST"])
def submit_word():
    selected_word = request.form["selectedWord"]
    word_definition = request.form["wordDefinition"]
    sentence_id = request.form["sentenceId"]
    if selected_word and word_definition and sentence_id:
        with get_db_connection() as db:
            db.execute(
                "INSERT INTO words (word, definition, sentence_id) VALUES (?, ?, ?)",
                [selected_word, word_definition, sentence_id],
            )
            db.commit()
    return redirect(url_for("main.home"))


@main_bp.route("/sentences")
def show_sentences():
    with get_db_connection() as db:
        cur = db.execute("SELECT content FROM sentences order by id desc")
        sentences = cur.fetchall()
        sentences = [parse_sentence(row) for row in sentences]
        return render_template("sentences.html", sentences=sentences)


@main_bp.route("/query_word/en")
def query_word():
    word = request.args.get("word")
    if word is None:
        return "No word provided"
    return mdict.lookup(word)


@main_bp.route("/query_word/<path:path>")
def get_resource(path):
    return mdict.lookup(path)


@main_bp.route("/words")
def show_words():
    with get_db_connection() as db:
        cur = db.execute(
            "SELECT w.id,word,s.content, definition FROM words w LEFT JOIN sentences s ON w.sentence_id = s.id order by w.id desc"
        )
        words = cur.fetchall()
        return render_template("words.html", words=words)


@main_bp.route("/delete_word/<int:word_id>", methods=["POST"])
def delete_word(word_id):
    with get_db_connection() as db:
        db.execute("DELETE FROM words WHERE id = ?", (word_id,))
        db.commit()
        # conn.close()
        return redirect(url_for("word_list"))


@main_bp.route("/manage_sentences")
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
        # breakpoint()
        return render_template("manage_sentences.html", sentences=sentences)


@main_bp.route("/delete_sentence/<int:sentence_id>")
def delete_sentence(sentence_id):
    with get_db_connection() as db:
        db.execute("DELETE FROM sentences WHERE id = ?", (sentence_id,))
        db.commit()
        return redirect(url_for("main.manage_sentences"))
