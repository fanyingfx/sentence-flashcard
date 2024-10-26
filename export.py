from datetime import datetime
import sqlite3
import csv

TODAY_STR = datetime.today().strftime("%Y-%m-%d")
DATABASE_NAME = f"databases/{TODAY_STR}.sentences.db"
db = sqlite3.connect(DATABASE_NAME)


def emphasize_word(word_attrs):
    word = word_attrs[0]
    content: str = word_attrs[1]
    definition = word_attrs[2]
    description = word_attrs[3]

    content = content.replace(word, f"<b>{word}</b>")
    return (word, content, definition, description)


def save_file(words):
    # add # to indicate it's the header
    # https://docs.ankiweb.net/importing/text-files.html#file-headers

    fieldnames = ["#word", "sentence", "definition", "description"]
    with open("sentence.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        writer.writerows(word for word in words if word[1])


cur = db.execute(
    "SELECT words.word,sentences.content, definition,sentences.descriptions FROM words  LEFT JOIN sentences  ON words.sentence_id = sentences.id order by words.id desc"
)

words = cur.fetchall()
if not words:
    print("db is empty")
    exit(1)
words = [emphasize_word(word) for word in words]
save_file(words)
