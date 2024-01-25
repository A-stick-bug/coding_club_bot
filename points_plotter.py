# for fetching data
import requests
import os
from dotenv import load_dotenv
from collections import defaultdict
import json

# for plotting
import matplotlib.pyplot as plt


def fetch_submission(user: str, api_key: str, page: int) -> dict:
    url = f"https://dmoj.ca/api/v2/submissions?user={user}&page={page}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers)
    return response.json()


def fetch_raw_point_history(user: str, api_key: str):
    """
    get the data for the plotter
    plotted data: total points before balancing
    """

    data = fetch_submission(user, api_key, 1)  # get number of submission pages
    n_pages = data["data"]["total_pages"]

    best = defaultdict(int)  # best points for each question
    point_gains = []  # (times when points were gained, new point value)
    total = 0
    for page in range(1, n_pages + 1):  # process each page (need multiple requests)
        data = fetch_submission(user, api_key, page)
        submissions = data["data"]["objects"]

        for sub in submissions:  # process each submission
            problem = sub["problem"]
            date = sub["date"].split("T")[0]
            points = sub["points"] if sub["points"] != None else 0

            if problem not in best or best[problem] < points:  # gained points at this time
                diff = points - best[problem]  # get point gained
                total += diff
                best[problem] = points
                point_gains.append((date, total))

    return point_gains


def fetch_point_history(user: str, api_key: str):
    """
    get the data for the plotter
    plotted data: balanced points (after aplying formula)
    """
    def balance(questions):
        """applies formula to points based on question values"""
        bal = sorted(questions.values(), reverse=True)  # sort by point worth
        P = sum((0.95 ** i) * bal[i] for i in range(0, min(100, len(bal))))
        B = 150 * (1 - 0.997 ** len(ac))
        return P + B

    data = fetch_submission(user, api_key, 1)  # get number of submission pages
    n_pages = data["data"]["total_pages"]

    best = defaultdict(int)  # best points for each question
    point_gains = []  # (times when points were gained, new point value)
    ac = set()
    for page in range(1, n_pages + 1):  # process each page (need multiple requests)
        data = fetch_submission(user, api_key, page)
        submissions = data["data"]["objects"]

        for sub in submissions:  # process each submission
            problem = sub["problem"]
            date = sub["date"].split("T")[0]
            points = sub["points"] if sub["points"] != None else 0

            if problem not in best or best[problem] < points:  # gained points at this time
                if sub["result"] == "AC":  # solved new problem
                    ac.add(problem)
                best[problem] = points
                point_gains.append((date, balance(best)))

    return point_gains


def fetch_mock_data():
    """
    :return: balanced points based on mock data
    """
    def balance(questions):
        """applies formula to points based on question values"""
        bal = sorted(questions.values(), reverse=True)  # sort by point worth
        P = sum((0.95 ** i) * bal[i] for i in range(0, min(100, len(bal))))
        B = 150 * (1 - 0.997 ** len(ac))
        return P + B

    with open("dummy_submissions.json", "r") as dummy_data:
        data = json.load(dummy_data)

    submissions = data["data"]["objects"]
    best = defaultdict(int)  # best points for each question
    point_gains = []  # (times when points were gained, new point value)
    ac = set()

    for sub in submissions:  # process each submission
        problem = sub["problem"]
        date = sub["date"].split("T")[0]
        points = sub["points"] if sub["points"] != "None" else 0

        if problem not in best or best[problem] < points:  # gained points at this time
            if sub["result"] == "AC":  # solved new problem
                ac.add(problem)
            best[problem] = points
            point_gains.append((date, balance(best)))
    return point_gains


def plot_points(history: list, name: str):
    """
    saves a picture of the graph
    """
    x = list(map(lambda x: x[0], history))
    y = list(map(lambda x: x[1], history))
    plt.xlabel("Date")
    plt.ylabel("Points")
    plt.title(f"{name}'s Problems Progression")
    plt.plot(x, y)
    plt.savefig('point_graph.png')
    plt.close()


if __name__ == '__main__':
    TESTING = True
    user = "Ivan_Li"

    load_dotenv("environment/.env")  # load all the variables from the env file
    token = os.getenv("TOKEN")
    if TESTING:
        history = fetch_mock_data()
    else:
        history = fetch_point_history(user, token)

    plot_points(history, user)
