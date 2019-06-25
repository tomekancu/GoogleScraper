from django.conf import settings
import requests_html as rh
import re


class Result:
    def __init__(self, result_count: int, results: list):
        self.result_count = result_count
        self.results = results

    def __str__(self) -> str:
        return f"Results(count={self.result_count}, list={self.results})"


class Page:
    def __init__(self, index: int, title: str, dest: str, url: str):
        self.index = index
        self.title = title
        self.dest = dest
        self.url = url

    def __str__(self) -> str:
        return f"Page(i={self.index}, title={self.title}, dest={self.dest}, url={self.url})"


class GoogleSearchClient:

    def __init__(self, client: rh.BaseSession = None, headers: dict = None):
        if client is None:
            client = rh.HTMLSession()
        if headers is None:
            headers = {'User-Agent': settings.USER_AGENT}
        self.headers = headers
        self.client = client

    def get_results_for(self, query: str):
        if query is None:
            query = ""

        if len(query) == 0:
            raise ValueError("no query")

        r = self.client.get("https://www.google.pl/search", params={"q": query}, headers=self.headers, timeout=60)
        r.html.render()
        return self.get_results_from(r.html)

    @staticmethod
    def get_results_from(html: rh.HTML) -> Result:
        result_count = html.find("#resultStats", first=True).text
        result_count = re.sub(r"(\n.*$)|([^\d])", "", result_count)
        result_count = int(result_count)

        results = html.find("#search .srg .g")

        pages = []
        for i, g in enumerate(results):
            a = g.find(".r a", first=True)
            url = a.attrs["href"]
            title = a.find("h3", first=True).text
            dest = g.find(".s .st", first=True).text
            pages.append(Page(i + 1, title, dest, url))

        return Result(result_count, pages)
