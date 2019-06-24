from django.db import models

# Create your models here.


class Query(models.Model):
    query_text = models.CharField(max_length=200)
    user_ip = models.GenericIPAddressField()
    asked_date = models.DateTimeField()
    result_count = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.query_text} - {self.user_ip}"


class Page(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    nr = models.IntegerField(default=0)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    destription = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nr} - {self.title}"
