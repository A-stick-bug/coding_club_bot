# for fetching data
import requests
import os
from dotenv import load_dotenv
from collections import defaultdict
import json

# for plotting
import matplotlib.pyplot as plt
import datetime as dt

from dmoj_utils import balance

load_dotenv("environment/.env")  # load all the variables from the env file
api_key = os.getenv("DMOJ_PASSWORD")


def fetch_submission(user: str, page: int) -> dict:
    url = f"https://dmoj.ca/api/v2/submissions?user={user}&page={page}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers)
    return response.json()


def fetch_raw_point_history(user: str):
    """
    get the data for the plotter
    plotted data: total points before balancing
    """

    data = fetch_submission(user, 1)  # get number of submission pages
    n_pages = data["data"]["total_pages"]

    best = defaultdict(int)  # best points for each question
    point_gains = []  # (times when points were gained, new point value)
    total = 0
    for page in range(1, n_pages + 1):  # process each page (need multiple requests)
        data = fetch_submission(user, page)
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


def fetch_point_history(user: str):
    """
    get the data for the plotter
    plotted data: balanced points (after applying formula)
    """

    data = fetch_submission(user, 1)  # get number of submission pages
    n_pages = data["data"]["total_pages"]

    best = defaultdict(int)  # best points for each question
    point_gains = []  # (times when points were gained, new point value)
    ac = set()
    for page in range(1, n_pages + 1):  # process each page (need multiple requests)
        data = fetch_submission(user, page)
        submissions = data["data"]["objects"]

        for sub in submissions:  # process each submission
            problem = sub["problem"]
            date = sub["date"].split("T")[0]
            points = sub["points"] if sub["points"] != None else 0

            if problem not in best or best[problem] < points:  # gained points at this time
                if sub["result"] == "AC":  # solved new problem
                    ac.add(problem)
                best[problem] = points
                point_gains.append((date, balance(best, ac)))

    return point_gains


def fetch_problem_history(user: str):
    """
    get a user's history of problems solved
    """
    data = fetch_submission(user, 1)  # get number of submission pages
    n_pages = data["data"]["total_pages"]

    problems_solved = []  # (times when problems were solved, new problems solved)
    ac = set()
    for page in range(1, n_pages + 1):  # process each page (need multiple requests)
        data = fetch_submission(user, page)
        submissions = data["data"]["objects"]

        for sub in submissions:  # process each submission
            problem = sub["problem"]
            date = sub["date"].split("T")[0]
            if sub["result"] == "AC" and problem not in ac:  # solved new problem
                ac.add(problem)
                problems_solved.append((date, len(ac)))

    return problems_solved


def fetch_mock_data():
    """
    :return: balanced points based on mock data
    """

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
            point_gains.append((date, balance(best, ac)))
    return point_gains


def plot_points(history: list, name: str, y_text: str, title: str):
    """
    saves a picture of the graph
    """
    x = [dt.datetime.strptime(d[0], '%Y-%m-%d').date() for d in history]  # extract time as datetime
    y = list(map(lambda x: x[1], history))

    # labels
    plt.xlabel("Date", fontsize=9)
    plt.ylabel(y_text)
    plt.title(f"{name}'s {title}")
    plt.grid(color="silver")
    plt.xticks(rotation=13, fontsize=8.5)  # rotate to prevent overlap in text

    # save plot as image
    plt.plot(x, y, label=f"{name} ({round(history[-1][1], 2)})")
    plt.legend(loc="upper left")
    plt.savefig('point_graph.png')
    plt.close()


if __name__ == '__main__':
    TESTING = 0
    user = "Ivan_Li"

    load_dotenv("environment/.env")  # load all the variables from the env file
    token = os.getenv("DMOJ_PASSWORD")
    if TESTING:
        history = fetch_mock_data()
    else:
        history = fetch_problem_history(user)

    # plot points
    plot_points(history, user, "Points", "Points Progression")

    # # plot problems solved
    # plot_points(history, user, "Problems Solved", "Problems Progression")
