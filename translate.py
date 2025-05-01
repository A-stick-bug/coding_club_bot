import requests
import json
import urllib.parse

def translate_text(text, source_language="auto", target_language="en"):
    text = text.replace("|"," ")
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + source_language + "&tl=" + target_language + "&dt=t&q=" + urllib.parse.quote(text, safe='')
    response = requests.get(url)
    response_text = json.loads(response.text)
    translated_text = response_text[0][0][0]
    return translated_text
