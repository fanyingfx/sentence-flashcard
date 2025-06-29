import json
import requests
import re

def invoke(action, **params):
    res=requests.post("http://localhost:8765", json={
        "action": action,
        "version": 6,
        "params": params
    }).json()
    return res

def get_cards_from_deck(deck_name):
    # 获取该 deck 中所有卡片的 ID
    result = invoke("findCards", query=f'deck:"{deck_name}"')
    card_ids = result.get("result", [])

    if not card_ids:
        return []

    # 获取详细卡片信息
    cards_info = invoke("cardsInfo", cards=card_ids)
    return cards_info.get("result", [])
def update_note_fields(note_id, new_fields):
    """
    note_id: int, the ID of the note
    new_fields: dict, e.g. {"Front": "New front text", "Back": "New back text"}
    """
    result = invoke("updateNoteFields", note={
        "id": note_id,
        "fields": new_fields
    })
    return result
HYPER_TTS='[sound:hypertts'
def update_odh_fields(card:dict):
    res = {k:v['value'] for k,v in card.items()}
    sentence:str = card['sentence']['value']
    if '[sound:hypertts-'in sentence:
        # print(sentence.split('[sound:hypertts-'))
        index = sentence.rfind(HYPER_TTS)
        sentence_audio = sentence[index:]
        sentence_str= sentence[:index]
        res['sentence']=sentence_str
        res['sentence-audio']=sentence_audio



    return res
# 示例使用
deck_name = "English::ODH"  # 替换成你自己的 deck 名
cards = get_cards_from_deck(deck_name)

error_cnt=0
for card in cards:
    fields=card['fields']
    updated_fields=update_odh_fields(fields)
    res=update_note_fields(card['cardId'],updated_fields)    # print(f"Card ID: {card['cardId']}")
    if res['error'] is not None:
        print(res)
        error_cnt+=1
        continue
print(f"error Count: {error_cnt}")
