from django.http import HttpResponseRedirect
from django.shortcuts import render

from . import apps
from . import models

import logging

logger = logging.getLogger("root")


# Create your views here.


def index(request):
    logger.info("index")
    return render(request, 'index.html', {"app_title": apps.AppConfig.verbose_name})


def query(request):
    try:
        ip: str = request.META['REMOTE_ADDR']
        q: str = request.POST["query"]
        q = q.strip()
        if len(q) == 0:
            raise ValueError("no query")
        logger.info(f"ip {ip} query {q}")
        my_query = models.get_query_for(q, ip)
        logger.info(f"querys {my_query}")
        for p in my_query.page_set.all():
            print(p)
    except KeyError:
        logger.error("no query")
        return HttpResponseRedirect("/")
    except ValueError:
        logger.error("no results")
        return render(request, 'index.html', {"app_title": apps.AppConfig.verbose_name,
                                              "q": q,
                                              "query": None})
    else:
        return render(request, 'index.html', {"app_title": apps.AppConfig.verbose_name,
                                              "q": q,
                                              "query": my_query})
