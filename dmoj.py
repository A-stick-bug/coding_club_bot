import requests
from bs4 import BeautifulSoup
from typing import Union

from user_data import UserData, get_user_data

# change to your own key if needed
user_base = "https://dmoj.ca/api/v2/user/"


def fetch_ccc(user: str, api_key: str):
    """dead function since no one will bother sending their API key every time, just use the web scraper below"""
    url = user_base + user
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers)
    data = response.json()

    problems = data["data"]["object"]["solved_problems"]
    ccc = [p for p in problems if p.startswith("ccc")]

    return len(ccc), ccc


def fetch_points(dmoj_username: str) -> int:
    """
    Returns how many CCC/CCO points a DMOJ user has.
    """
    url = f"https://dmoj.ca/user/{dmoj_username}/solved"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    valid_groups = ["CCC", "CCO"]

    groups = soup.find_all(class_='unselectable toggle closed')
    total = 0
    for group in groups:
        s = group.text.replace("(", "").split()
        if s[0] in valid_groups:
            total += int(round(float(s[1]), 0))
    return total


def connect_account(user_id: int, dmoj_username: str) -> None:
    """
    Connects a Discord account to a DMOJ account.
    """
    dmoj_username = dmoj_username.replace(" ", "_")
    
    user_data = get_user_data(user_id)
    if user_data is not None:
        user_data.dmoj_username = dmoj_username
    else:
        user_data = UserData(
            user_id=user_id,
            dmoj_username=dmoj_username,
            level=0,
            experience=0,
            messages=0,
            next_experience_gain_time=0
        )
    
    user_data.save_to_db()
