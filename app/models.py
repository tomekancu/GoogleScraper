from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django.db import models
from typing import Tuple, List

from . import google_search as gs
from collections import Counter


# Create your models here.


class Query(models.Model):
    query_text = models.CharField(max_length=200)
    user_ip = models.GenericIPAddressField()
    asked_date = models.DateTimeField()
    result_count = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.query_text} - {self.user_ip}"

    def get_ordered_pages(self) -> QuerySet:
        return self.page_set.order_by("nr").all()

    def get_stats(self, n=10) -> List[Tuple[str, int]]:
        whole_text = " ".join(f"{page.title} {page.destription}" for page in self.get_ordered_pages())
        words = filter(lambda x: len(x.strip()) > 0 and x.isalnum(), whole_text.split())
        counter = Counter(words)
        return counter.most_common(n)


class Page(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    nr = models.IntegerField(default=0)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    destription = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nr} - {self.title}"


def get_query_for(q: str, ip: str, timedelta: float = settings.TIME_DELTA_CLIENT_IN_SECONDS,
                  google_search_client: gs.GoogleSearchClient = gs.GoogleSearchClient()) -> Query:
    my_query = Query.objects.filter(query_text=q, user_ip=ip,
                                    asked_date__gte=timezone.now() - timezone.timedelta(seconds=timedelta)) \
        .order_by('-asked_date').first()
    if my_query is None:
        results = google_search_client.get_results_for(q)

        my_query = Query.objects.create(
            query_text=q, user_ip=ip,
            asked_date=timezone.now(),
            result_count=results.result_count,
        )

        for page in results.results:
            Page.objects.create(query=my_query, nr=page.index, url=page.url, title=page.title, destription=page.dest)

    return my_query
