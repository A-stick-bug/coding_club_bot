# for fetching data
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

import json
import time
from collections import defaultdict

# for plotting
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

load_dotenv("environment/.env")  # load all the variables from the env file
api_key = os.getenv("DMOJ_PASSWORD")
PAGES = 160  # max pages on DMOJ
CATEGORIES = ["Data Structures", "Greedy Algorithms", "Ad Hoc",
              "Math", "String Algorithms", "Graph Theory", "Dynamic Programming"]


def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` Axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding Axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):

        def transform_path_non_affine(self, path):
            # Paths with non-unit interpolation steps correspond to gridlines,
            # in which case we force interpolation (to defeat PolarTransform's
            # autoconversion to circular arcs).
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):

        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def update_problem_info():
    """Go through all problems on DMOJ and store their types"""
    type_table = {}
    for i in range(1, PAGES + 1):  # go through all pages on DMOJ
        try:
            url = f"https://dmoj.ca/problems/?show_types=1&page={i}"
            html_content = requests.get(url).text
        except:  # all pages visited
            break
        soup = BeautifulSoup(html_content, features="html.parser")

        for row in soup.find_all("td", class_="problem"):
            url_element = row.find("a")
            problem_url = url_element["href"].split("/")[-1]

            types_element = row.parent.find_next("td", class_="types")
            tags = [t.text for t in types_element.find_all("span")]
            type_table[problem_url] = tags

        print(f"finished page {i}/{PAGES}")
        time.sleep(1)  # prevent rate limit

    with open("problem_info.json", "w") as problem_types:
        json.dump(type_table, problem_types)
    print("Successfully saved data")


def get_user_problem_types(user: str):
    """Returns how many problems of each type a user has solved"""
    url = f"https://dmoj.ca/api/v2/user/{user}"

    headers = {"Authorization": f"Bearer {api_key}"}
    user = requests.get(url, headers).json()
    problems = user["data"]["object"]["solved_problems"]

    with open("problem_info.json", "r") as problem_types:
        type_table = json.load(problem_types)
    total = defaultdict(int)
    for p in problems:
        if p not in type_table:
            raise KeyError(f"Problem code '{p}' not found. 'problem_info.json' may be outdated.")
        types = type_table[p]

        for t in types:
            if "Math" in t:  # combine all 3 math categories
                total["Math"] += 1
            else:
                total[t] += 1
    return total


def plot_problem_types(users):
    """Generate a plot """
    if len(users) > 5:
        raise Exception("Too many users (5 max)")
    N = len(CATEGORIES)
    theta = radar_factory(N, frame='polygon')

    # get each user's type data
    data = []
    for user in users:
        user = get_user_problem_types(user)
        data.append([user[i] for i in CATEGORIES])
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))

    # plot each person's data
    for d in data:
        ax.plot(theta, d)
        ax.fill(theta, d, alpha=0.09, label='_nolegend_')
    ax.set_varlabels(CATEGORIES)

    # legend for each user's color
    ax.legend(users, loc=(-0.15, 0.9), fontsize="medium")
    plt.savefig("problem_types_graph.png")
    # plt.show()  # uncomment when testing
    plt.close()


if __name__ == '__main__':
    update_problem_info()
