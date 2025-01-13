from django.db import models


class Vacancy(models.Model):
    name = models.CharField(max_length=255)
    key_skills = models.TextField()
    salary_from = models.IntegerField(null=True, blank=True)
    salary_to = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10, null=True, blank=True)
    area_name = models.CharField(max_length=255, null=True, blank=True)
    published_at = models.DateTimeField()

    class Meta:
        db_table = 'vacancies'

