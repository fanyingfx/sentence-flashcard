from flask import Blueprint, jsonify, redirect, request, url_for, render_template

from ..models import get_db_connection, TODAY_STR
from ..language import english

sentence_bp = Blueprint("sentence", __name__, url_prefix="/sentence")


@sentence_bp.route("/manage")
def manage_sentences():
    with get_db_connection() as conn:
        sentences = conn.execute(
            f"SELECT id,content,descriptions FROM sentences  order by id desc limit 20"
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


@sentence_bp.route("/submit", methods=["POST"])
def submit_json():
    data = request.get_json()
    sentence = data.get("sentence")
    descriptions = data.get("descriptions")

    if sentence:
        with get_db_connection() as db:
            db.execute(
                "INSERT INTO sentences (content,descriptions) VALUES (?,?)",
                [sentence, descriptions],
            )
            db.commit()
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "Sentence is required"}), 400
