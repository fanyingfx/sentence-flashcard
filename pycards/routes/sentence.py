from dataclasses import dataclass
from pathlib import Path
from flask import Blueprint, request, redirect, url_for, render_template

from ..models import get_db_connection
from ..language import english

sentence_bp = Blueprint("sentence", __name__, url_prefix="/sentence")




@sentence_bp.route("/manage")
def manage_sentences():
    with get_db_connection() as conn:
        sentences = conn.execute(
            "SELECT id,content,descriptions FROM sentences order by id desc"
        ).fetchall()
        conn.close()
        sentences = [
            english.DBSentence(sentence_id=row[0], content=row[1], descriptions=row[2])
            for row in sentences
        ]
        return render_template("manage_sentences.html", sentences=sentences)


@sentence_bp.route("/delete/<int:sentence_id>")
def delete_sentence(sentence_id):
    with get_db_connection() as db:
        db.execute("DELETE FROM sentences WHERE id = ?", (sentence_id,))
        db.commit()
        return redirect(url_for("sentence.manage_sentences"))
