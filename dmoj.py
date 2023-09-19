import requests
from bs4 import BeautifulSoup
import json

# change to your own key if needed
user_base = "https://dmoj.ca/api/v2/user/"


def fetch_ccc(user: str, api_key: str):
    url = user_base + user
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers)
    data = response.json()

    problems = data["data"]["object"]["solved_problems"]
    ccc = [p for p in problems if p.startswith("ccc")]

    return len(ccc), ccc


def fetch_points(user: str):
    url = f"https://dmoj.ca/user/{user}/solved"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    groups = soup.find_all(class_='unselectable toggle closed')
    for group in groups:
        s = group.text.replace("(", "").split()
        if s[0] == "CCC":
            return s[1]
    return 0


def connect_account(id: int, dmoj_user: str):
    with open('database.json', 'r') as f:
        db = json.load(f)

    db[id] = dmoj_user  # store DMOJ username by ID

    with open('database.json', 'w') as f:
        json.dump(db, f)


# testing
if __name__ == '__main__':
    ...
