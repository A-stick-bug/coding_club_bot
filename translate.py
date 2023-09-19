import requests
import json

def translate_text(text, target_language):
    text = text.replace("|"," ")
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=" + target_language + "&dt=t&q=" + text
    response = requests.get(url)
    response_text = json.loads(response.text)
    translated_text = response_text[0][0][0]
    return translated_text
