from datetime import datetime
import sqlite3
import requests

TODAY_STR = datetime.today().strftime("%Y-%m-%d")
# DATABASE_NAME = f"databases/{TODAY_STR}.sentences.db"
DATABASE_NAME = "sentences.db"


def emphasize_word(word_attrs):
    word = word_attrs[0]
    content: str = word_attrs[1]
    definition = word_attrs[2]
    description = word_attrs[3]

    content = content.replace(word, f"<b>{word}</b>")
    return (word, content, definition, description)


def add_notes_to_anki(words):
    notes = []
    for word in words:
        note = {
            "deckName": "English::Sentences",
            "modelName": "MySentence",
            "fields": {
                "word": word[0],
                "sentence": word[1],
                "definition": word[2],
                "description": word[3],
            },
            "tags": [],
            "options": {
                "allowDuplicate": True,
            },
        }
        notes.append(note)

    payload = {"action": "addNotes", "version": 6, "params": {"notes": notes}}

    response = requests.post("http://localhost:8765", json=payload)
    result = response.json()
    if result.get("error"):
        raise Exception(f"Error: {result['error']}")
    else:
        print("Notes added successfully")


if __name__ == "__main__":
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.execute(
        "SELECT words.word, sentences.content, words.definition, sentences.descriptions,words.id FROM words LEFT JOIN sentences ON words.sentence_id = sentences.id WHERE words.export_status = 0 ORDER BY words.id DESC"
    )

    words = cur.fetchall()
    if not words:
        print("No new Words")
        exit(1)
    word_ids = [word[4] for word in words]
    words = [emphasize_word(word) for word in words]
    add_notes_to_anki(words)
    cur.executemany(
        "UPDATE words SET export_status = 1 WHERE id = ?",
        [(word_id,) for word_id in word_ids],
    )
    db.commit()
    db.close()
