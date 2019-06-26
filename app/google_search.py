import re
import urllib.parse
from typing import List

import bs4
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Page:
    def __init__(self, index: int, title: str, dest: str, url: str):
        self.index = index
        self.title = title
        self.dest = dest
        self.url = url

    def __str__(self) -> str:
        return f"Page(i={self.index}, title={self.title}, dest={self.dest}, url={self.url})"


class Result:
    def __init__(self, result_count: int, results: List[Page]):
        self.result_count = result_count
        self.results = results

    def __str__(self) -> str:
        return f"Results(count={self.result_count}, list={self.results})"


class GoogleSearchClient:

    def __init__(self, user_agent: str = settings.USER_AGENT):
        self.user_agent = user_agent

    def get_results_for(self, query: str):
        if query is None:
            query = ""

        if len(query) == 0:
            raise ValueError("no query")

        url = "https://www.google.pl/search?" + urllib.parse.urlencode({'q': query})

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument(f'user-agent={self.user_agent}')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(url)

        # It can be a good idea to wait for a few seconds before trying to parse the page
        # to ensure that the page has loaded completely.
        browser.implicitly_wait(3)

        soup = bs4.BeautifulSoup(browser.page_source, 'html.parser')
        browser.quit()

        return self.get_results_from(soup)

    @staticmethod
    def get_results_from(html: bs4.BeautifulSoup) -> Result:
        result_stats = html.select_one("#resultStats")
        if result_stats is None:
            raise ValueError("no result stats in html")

        result_count = result_stats.get_text(separator="\n")
        result_count = re.sub(r"(\n.*$)|([^\d])", "", result_count)
        result_count = int(result_count)

        results = html.select("#search .g")

        pages = []
        for i, g in enumerate(results):
            a = g.select_one(".r a")
            if a is None:
                continue
            url = a.attrs["href"]
            h3 = a.select_one("h3")
            if h3 is None:
                continue
            title = h3.get_text()

            destelements = g.select_one(".s .st")
            if destelements is None:
                continue
            dest = destelements.get_text()
            pages.append(Page(i + 1, title, dest, url))

        return Result(result_count, pages)
