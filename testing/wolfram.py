import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium import webdriver

import time


def query(question):
    url = f"https://wolfreealpha.netlify.app/input/?i={question}&lang=en"

    options = webdriver.EdgeOptions()
    #options.add_argument('--headless')

    browser = webdriver.Chrome(options=options)
    browser.get(url)
    time.sleep(3)
    html = browser.page_source
    soup = BeautifulSoup(html, features="html.parser")

    main_container = soup.find_all('div', class_="wolfree-pods")  # first and only main container
    print(main_container)
    # print(parser)


if __name__ == '__main__':
    query("derivative of x^2")
