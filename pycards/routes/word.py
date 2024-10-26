from flask import Blueprint, request, redirect, url_for, render_template

from pycards.mdict_query.mdict_utils import MDXDict
from ..models import get_db_connection
from ..language import english

word_bp = Blueprint("word", __name__, url_prefix="/word")


@word_bp.route("/submit_word", methods=["POST"])
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


@word_bp.route("/query/en")
def query_word():
    word = request.args.get("word")
    if word is None:
        return "No word provided"
    return english.mdict.lookup(word)


@word_bp.route("/query/<path:path>")
def get_resource(path):
    return english.mdict.lookup(path)


def emphasize_word(word_attrs):
    # id,word,content,definition,description
    id = word_attrs[0]
    word = word_attrs[1]
    content: str = word_attrs[2]
    definition = word_attrs[3]
    description = word_attrs[4]

    if content is not None:
        content = content.replace(word, f"<b>{word}</b>")
    return (id, word, content, definition, description)


@word_bp.route("/words")
def show_words():
    with get_db_connection() as db:
        cur = db.execute(
            "SELECT words.id,words.word,sentences.content, definition,sentences.descriptions FROM words  LEFT JOIN sentences  ON words.sentence_id = sentences.id order by words.id desc"
        )
        words = cur.fetchall()
        words = [emphasize_word(word) for word in words]
        return render_template("words.html", words=words)


@word_bp.route("/delete_word/<int:word_id>", methods=["GET"])
def delete_word(word_id):
    with get_db_connection() as db:
        db.execute("DELETE FROM words WHERE id = ?", (word_id,))
        db.commit()
        # conn.close()
        return redirect(url_for("word.show_words"))
