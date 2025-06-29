from flask import Blueprint, request, redirect, url_for, render_template
from ..models import get_db_connection, TODAY_STR

from ..language import english

home_bp = Blueprint("main", __name__)
# TODAY_STR= date.strftime("%Y-%m-%d")


@home_bp.route("/")
def home():
    sentences = []
    with get_db_connection() as db:
        cur = db.execute(
            f"""SELECT sentences.id,sentences.content,sentences.descriptions FROM sentences left join words on sentences.id = words.sentence_id
                    where create_date >= '{TODAY_STR}'    or words.sentence_id is NULL
                order by sentences.id desc"""
        )
        sentences = cur.fetchall()
        sentences = [english.parse_sentence(row) for row in sentences]
    return render_template("home.html", sentences=sentences)


@home_bp.route("/submit", methods=["POST"])
def submit():
    sentence = request.form["sentence"]
    descriptions = request.form["descriptions"]

    if sentence:
        with get_db_connection() as db:
            db.execute(
                "INSERT INTO sentences (content,descriptions) VALUES (?,?)",
                [sentence, descriptions],
            )
            db.commit()
    return redirect(url_for("main.home"))
