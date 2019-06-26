from django.test import TestCase
from unittest.mock import MagicMock
from django.utils import timezone
import bs4

from .models import Query, Page, get_query_for
from .google_search import GoogleSearchClient, GoogleQueryResult, GooglePageResult


# Create your tests here.


class QuestionModelTests(TestCase):

    def setUp(self):
        query1 = Query.objects.create(query_text="lion", user_ip="127.0.0.1",
                                      asked_date=timezone.now() - timezone.timedelta(seconds=61), result_count=600_001)
        for i in range(6):
            Page.objects.create(query=query1, nr=i + 1, url="http://google.pl", title=f"Title {i}",
                                destription=f"Dest{i} ha hi")

        query2 = Query.objects.create(query_text="mamba", user_ip="127.0.0.1",
                                      asked_date=timezone.now() - timezone.timedelta(seconds=30), result_count=600_000)
        for i in range(4):
            Page.objects.create(query=query2, nr=i + 1, url="http://google.pl", title=f"Title {i}",
                                destription=f"Dest{i} ha hi")

        query3 = Query.objects.create(query_text="mamba2", user_ip="127.0.0.2",
                                      asked_date=timezone.now() - timezone.timedelta(seconds=30), result_count=600_002)
        for i in range(5):
            Page.objects.create(query=query3, nr=i + 1, url="http://google.pl", title=f"Title {i}",
                                destription=f"Dest{i} ha hi")

    def test_download_results_bad_time(self):
        google_client = GoogleSearchClient()
        google_client.get_results_for = MagicMock(return_value=GoogleQueryResult(100_000, [
            GooglePageResult(1, "Title 1", "Dest 1", "http://google.pl"),
            GooglePageResult(1, "Title 2", "Dest 2", "http://google.pl"),
            GooglePageResult(1, "Title 3", "Dest 3", "http://google.pl")
        ]))

        query = get_query_for("lion", "127.0.0.1", 60, google_client)

        google_client.get_results_for.assert_called_with("lion")

        if query is None:
            self.fail()
        self.assertEqual(query.query_text, 'lion')
        self.assertEqual(query.result_count, 100_000)
        self.assertEqual(query.page_set.count(), 3)

    def test_download_results_bad_ip(self):
        google_client = GoogleSearchClient()
        google_client.get_results_for = MagicMock(return_value=GoogleQueryResult(100_000, [
            GooglePageResult(1, "Title 1", "Dest 1", "http://google.pl"),
            GooglePageResult(1, "Title 2", "Dest 2", "http://google.pl"),
            GooglePageResult(1, "Title 3", "Dest 3", "http://google.pl")
        ]))

        query = get_query_for("mamba2", "127.0.0.3", 1000, google_client)

        google_client.get_results_for.assert_called_with("mamba2")

        if query is None:
            self.fail()
        self.assertEqual(query.query_text, 'mamba2')
        self.assertEqual(query.result_count, 100_000)
        self.assertEqual(query.page_set.count(), 3)

    def test_database_results(self):
        google_client = GoogleSearchClient()
        google_client.get_results_for = MagicMock(return_value=GoogleQueryResult(100_000, []))

        query = get_query_for("mamba", "127.0.0.1", 60, google_client)

        google_client.get_results_for.assert_not_called()

        if query is None:
            self.fail()
        self.assertEqual(query.query_text, 'mamba')
        self.assertEqual(query.result_count, 600_000)
        self.assertEqual(query.page_set.count(), 4)

    def test_statistics(self):
        query = Query.objects.get(query_text="lion", user_ip="127.0.0.1")

        stats = query.get_stats(5)
        self.assertEqual(len(stats), 5)
        self.assertIn(("Title", 6), stats)
        self.assertIn(("ha", 6), stats)
        self.assertIn(("hi", 6), stats)
        self.assertIn(("0", 1), stats)

    def test_get_results_from(self):
        soup = bs4.BeautifulSoup("""
        <html>
        <head></head>
        <body>
            <div id="resultStats">Około 9&nbsp;700&nbsp;000&nbsp;000 wyników<nobr> (0,48 s)&nbsp;</nobr></div>
            <div id="search">
                <div class="g">
                    <div class="rc">
                        <div class="r">
                            <a href="http://poznan.ap.gov.pl/">
                                <h3 class="LC20lb">Archiwum P</h3>
                            </a>
                        </div>
                        <div class="s">
                            <div>
                                <span class="st">Godziny f</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """, 'html.parser')
        result = GoogleSearchClient.get_results_from(soup)
        self.assertEqual(result.result_count, 9_700_000_000)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].index, 1)
        self.assertEqual(result.results[0].title, "Archiwum P")
        self.assertEqual(result.results[0].url, "http://poznan.ap.gov.pl/")
        self.assertEqual(result.results[0].dest, "Godziny f")
