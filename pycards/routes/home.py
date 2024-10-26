# from dataclasses import dataclass
from flask import Blueprint, request, redirect, url_for, render_template
from ..models import get_db_connection

from ..language.english import parse_sentence

home_bp = Blueprint("main", __name__)


@home_bp.route("/")
def home():
    return render_home()


def render_home(keep_descriptions=False):
    with get_db_connection() as db:
        cur = db.execute(
            "SELECT id,content,descriptions FROM sentences order by id desc"
        )
        sentences = cur.fetchall()
        sentences = [parse_sentence(row) for row in sentences]
        return render_template("home.html", sentences=sentences)


@home_bp.route("/submit", methods=["POST"])
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
