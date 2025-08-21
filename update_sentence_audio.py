import httpx
import edge_tts
import os
import shutil
from pathlib import Path
from datetime import datetime


def clean_word(word: str) -> str:
    res = []
    for ch in word:
        if ch.isalpha():
            res.append(ch)
    return "".join(res)


VOICE = "en-US-JennyNeural"


def gen_audio(word: str, sentence: str) -> str:
    CWD = os.getcwd()
    cleaned_word = clean_word(word)
    Path(f"{CWD}/audios").mkdir(exist_ok=True)

    date_str = datetime.today().strftime("%Y%m%d%H%M%S")
    word_sentence_file = f"{CWD}/audios/{cleaned_word}_odh_sentence_{date_str}.mp3"
    sentence_communicate = edge_tts.Communicate(sentence, VOICE)
    sentence_communicate.save_sync(word_sentence_file)
    return word_sentence_file


def invoke(action, **params):
    res = httpx.post(
        "http://localhost:8765", json={"action": action, "version": 6, "params": params}
    ).json()
    return res


def get_cards_from_deck(deck_name):
    result = invoke("findCards", query=f'deck:"{deck_name}"')
    card_ids = result.get("result", [])

    if not card_ids:
        return []

    cards_info = invoke("cardsInfo", cards=card_ids)
    return cards_info.get("result", [])


def update_note_fields(note_id, new_fields):
    """
    note_id: int, the ID of the note
    new_fields: dict, e.g. {"Front": "New front text", "Back": "New back text"}
    """
    result = invoke("updateNoteFields", note={"id": note_id, "fields": new_fields})
    return result


def get_cards_without_sentence_audio(cards: list) -> list:
    res = []
    for card in cards:
        fields = card["fields"]
        fields = {k: v["value"] for k, v in fields.items()}
        if fields["sentence-audio"].strip() == "":
            res.append(card)
    return res


def update_card_with_sentence_audio(card):
    fields = card["fields"]
    fields = {k: v["value"] for k, v in fields.items()}
    word: str = fields["expression"]
    sentence: str = fields["sentence"]
    note_id = card["note"]
    audio_full_path = gen_audio(word, sentence)
    audio_filename = audio_full_path.split("/")[-1]
    result = invoke(
        "updateNoteFields",
        note={
            "id": note_id,
            "fields": fields,
            "audio": [
                {
                    "path": audio_full_path,
                    "filename": audio_filename,
                    "fields": ["sentence-audio"],
                },
            ],
        },
    )
    return result


def update_sentence_audio():
    deck_name = "English::ODH"
    cards = get_cards_from_deck(deck_name)
    todo_cards = get_cards_without_sentence_audio(cards)
    error_words = []
    added_words = []
    for card in todo_cards:
        word = card["fields"]["expression"]["value"]
        result = update_card_with_sentence_audio(card)
        if result["error"] is not None:
            error_words.append(word)
            print(result)
        else:
            added_words.append(word)
    print(f"added Words: {added_words}")
    if error_words:
        print(f"error Words: {error_words}")


if __name__ == "__main__":
    update_sentence_audio()
    if Path('audios').exists():
        shutil.rmtree('audios')

