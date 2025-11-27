# for fetching data
import requests
import os
from dotenv import load_dotenv
from collections import defaultdict
import json

# for plotting
import matplotlib.pyplot as plt
import datetime as dt

load_dotenv("environment/.env")  # load all the variables from the env file
api_key = os.getenv("DMOJ_PASSWORD")
CATEGORIES = ["Data Structures", "Greedy Algorithms", "Ad Hoc",
              "Math", "String Algorithms", "Graph Theory", "Dynamic Programming", "Implementation"]

with open("testing/problem_info.json", "r") as p_info:
    problem_info = json.load(p_info)

# use interactive
import matplotlib
matplotlib.use("TkAgg")

def balance(questions, ac):
    """applies formula to points based on question values"""
    bal = sorted(questions.values(), reverse=True)  # sort by point worth
    P = sum((0.95 ** i) * bal[i] for i in range(0, min(100, len(bal))))
    B = 150 * (1 - 0.997 ** len(ac))
    return P + B


def fetch_submission(user: str, page: int) -> dict:
    url = f"https://dmoj.ca/api/v2/submissions?user={user}&page={page}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers)
    return response.json()


def fetch_point_history(user: str):
    """
    get the data for the plotter
    plotted data: balanced points (after applying formula)
    """

    data = fetch_submission(user, 1)  # get number of submission pages
    n_pages = data["data"]["total_pages"]

    categories = defaultdict(lambda: defaultdict(int))

    point_gains = defaultdict(list)  # category: (times when points were gained, new point value)
    ac = set()
    for page in range(1, n_pages + 1):  # process each page (need multiple requests)
        data = fetch_submission(user, page)
        submissions = data["data"]["objects"]

        for sub in submissions:  # process each submission
            problem = sub["problem"]
            date = sub["date"].split("T")[0]
            points = sub["points"] if sub["points"] is not None else 0
            p_categories = problem_info[problem]["types"]

            for p_cat in p_categories:
                if "Math" in p_cat:  # compress maths tags into 1
                    p_cat = "Math"
                if p_cat not in CATEGORIES:
                    continue
                if problem not in categories[p_cat] or categories[p_cat][problem] < points:  # gained points at this time
                    if sub["result"] == "AC":  # solved new problem
                        ac.add(problem)
                    categories[p_cat][problem] = points
                    point_gains[p_cat].append((date, balance(categories[p_cat], ac)))

    return point_gains


def plot_points(histories, name: str, y_text: str, title: str):
    """
    saves a picture of the graph
    """
    for category, history in histories.items():
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

    plt.legend(histories.keys(), loc="upper left")
    plt.savefig('point_graph.png')
    plt.show()
    # plt.close()


if __name__ == '__main__':
    user = "ivan_li"

    load_dotenv("environment/.env")  # load all the variables from the env file
    token = os.getenv("DMOJ_PASSWORD")
    history = fetch_point_history(user)

    # plot points
    plot_points(history, user, "Points", "Points Progression")

    # # plot problems solved
    # plot_points(history, user, "Problems Solved", "Problems Progression")
