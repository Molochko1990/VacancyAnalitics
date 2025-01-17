from django.db import models


class Vacancy(models.Model):
    name = models.CharField(max_length=255)
    key_skills = models.TextField()
    salary_from = models.IntegerField(null=True, blank=True)
    salary_to = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10, null=True, blank=True)
    area_name = models.CharField(max_length=255, null=True, blank=True)
    published_at = models.DateTimeField()
    exchange_rate_to_rub = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'vacancies'

