from django.contrib import admin

# Register your models here.

from .models import Query, Page


class QueryAdmin(admin.ModelAdmin):
    list_display = ('query_text', 'user_ip', 'result_count', 'asked_date')
    list_filter = ['asked_date']
    search_fields = ['query_text']


class PageAdmin(admin.ModelAdmin):
    list_display = ('query', 'nr', 'title')
    list_filter = ['nr']
    search_fields = ['title', 'destription', 'url']


admin.site.register(Query, QueryAdmin)
admin.site.register(Page, PageAdmin)
