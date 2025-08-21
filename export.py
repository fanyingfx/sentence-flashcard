import os
import sqlite3
import requests
import edge_tts
from datetime import datetime
from dataclasses import dataclass


@dataclass
class WordInfo:
    word: str
    sentence: str
    definition: str
    description: str

    def formated_sentence(self: "WordInfo") -> str:
        """emphasize word in sentenc"""

        return self.sentence.replace(self.word, f"<b>{self.word}</b>")


TODAY_STR = datetime.today().strftime("%Y-%m-%d")
DATABASE_NAME = "sentences.db"
VOICE = "en-US-JennyNeural"


def clean_word(word: str) -> str:
    res = []
    for ch in word:
        if ch.isalpha():
            res.append(ch)
    return "".join(res)


def gen_audio(word, sentence) -> tuple[str, str]:
    """
    https://github.com/rany2/edge-tts/blob/master/examples/sync_audio_gen_with_predefined_voice.py

    """
    CWD = os.getcwd()
    cleaned_word = clean_word(word)
    date_str = datetime.today().strftime("%Y%m%d%H%M%S")

    word_output_file = f"{CWD}/audios/{cleaned_word}_{date_str}.mp3"
    word_sentence_file = f"{CWD}/audios/{cleaned_word}_sentence_{date_Str}.mp3"
    word_communicate = edge_tts.Communicate(word, VOICE)
    word_communicate.save_sync(word_output_file)

    sentence_communicate = edge_tts.Communicate(sentence, VOICE)
    sentence_communicate.save_sync(word_sentence_file)
    return (word_output_file, word_sentence_file)


def add_notes_to_anki(word_infos: list[WordInfo]):
    notes = []
    for word_info in word_infos:
        (word_audio, sentence_audio) = gen_audio(word_info.word, word_info.sentence)
        word_filename = word_audio.split("/")[-1]
        sentence_filename = sentence_audio.split("/")[-1]

        note = {
            "deckName": "English::Sentences",
            "modelName": "MySentence",
            "fields": {
                "word": word_info.word,
                "sentence": word_info.formated_sentence(),
                "definition": word_info.definition,
                "description": word_info.description,
            },
            "tags": [],
            "options": {
                "allowDuplicate": True,
            },
            "audio": [
                {
                    "path": word_audio,
                    "filename": word_filename,
                    "fields": ["word-audio"],
                },
                {
                    "path": sentence_audio,
                    "filename": sentence_filename,
                    "fields": ["sentence-audio"],
                },
            ],
        }
        notes.append(note)

    payload = {"action": "addNotes", "version": 6, "params": {"notes": notes}}

    response = requests.post("http://localhost:8765", json=payload)
    result = response.json()
    if result.get("error"):
        raise Exception(f"Error: {result['error']}")
    else:
        print("Notes added successfully")
        print(f"Total count: {len(word_infos)}")


def main():
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.execute(
        "SELECT words.word, sentences.content, words.definition, sentences.descriptions,words.id FROM words LEFT JOIN sentences ON words.sentence_id = sentences.id WHERE words.export_status = 0 ORDER BY words.id DESC"
    )
    word_raws = cur.fetchall()
    if not word_raws:
        print("No new Words")
        exit(0)
    word_ids = [word[4] for word in word_raws]
    words = [
        WordInfo(
            word=word[0], sentence=word[1], definition=word[2], description=word[3]
        )
        for word in word_raws
    ]
    # words = [emphasize_word_in_sentence(word) for word in words]
    add_notes_to_anki(words)
    cur.executemany(
        "UPDATE words SET export_status = 1 WHERE id = ?",
        [(word_id,) for word_id in word_ids],
    )
    db.commit()
    db.close()


def add_note_demo():
    notes = []
    word = ("hello", "hello,world", "", "")
    word_text = "hello"
    sentence = "hello, world"
    (word_audio, sentence_audio) = gen_audio(word_text, sentence)
    word_filename = word_audio.split("/")[-1]
    sentence_filename = sentence_audio.split("/")[-1]

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
        "audio": [
            {"path": word_audio, "filename": word_filename, "fields": ["word-audio"]},
            {
                "path": sentence_audio,
                "filename": sentence_filename,
                "fields": ["sentence-audio"],
            },
        ],
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
    main()
