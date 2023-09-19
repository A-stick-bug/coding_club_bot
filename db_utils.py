import json


def fetch_id(user_id: int):
    user_id = str(user_id)
    with open('database.json', 'r') as f:
        db = json.load(f)

    if user_id not in db:
        return False
    return db[user_id]
