# services/vacancy_service.py
from datetime import datetime
from django.db.models import Avg, Count, F, Value, FloatField
from django.db.models.functions import Coalesce
from django.db import models
from ..models import Vacancy
from .central_bank_api import CBRApi
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class VacancyService:
    def __init__(self):
        self.cbr = CBRApi()
        self._currency_cache = {}

    def preload_currency_rates(self):
        # Фильтруем записи с пустыми значениями прямо в запросе
        unique_combinations = Vacancy.objects.filter(
            salary_currency__isnull=False,
            salary_currency__gt="",  # Исключаем пустые строки
            published_at__isnull=False,
        ).values_list("salary_currency", "published_at").distinct()

        logger.info(f"Найдено {len(unique_combinations)} валидных комбинаций для загрузки курсов валют")

        # Загружаем курсы валют для каждой комбинации
        rates = {}
        for currency, published_at in unique_combinations:
            if currency != "RUR":
                month_start = published_at.replace(day=1)
                rates[(currency, month_start)] = self.cbr.get_currency_rate(currency, month_start)

        return rates


    def get_avg_salary_by_year(self):
        """
        Рассчитать среднюю зарплату по годам.
        """
        self.preload_currency_rates()  # Предварительно загружаем курсы валют
        salary_data = defaultdict(list)

        vacancies = Vacancy.objects.all()
        for vacancy in vacancies:
            year = vacancy.published_at.year
            rate = self.get_currency_rate(vacancy.salary_currency, vacancy.published_at)

            salary_values = [v for v in [vacancy.salary_from, vacancy.salary_to] if v]
            if salary_values:
                avg_salary = sum(salary_values) / len(salary_values)
                salary_in_rub = avg_salary * rate
                salary_data[year].append(salary_in_rub)

        avg_salary_by_year = [
            {"year": year, "avg_salary": round(sum(salaries) / len(salaries), 2)}
            for year, salaries in salary_data.items()
            if salaries
        ]

        return avg_salary_by_year

    def get_vacancy_count_by_year(self):
        """
        Возвращает количество вакансий по годам.
        """
        vacancies = Vacancy.objects.annotate(
            year=F("published_at__year")
        ).values("year").annotate(
            count=Count("id")
        ).order_by("year")

        return list(vacancies)

    def get_salary_by_city(self):
        """
        Рассчитать среднюю зарплату по городам с учётом конвертации валют.
        """
        self.preload_currency_rates()  # Предварительно загружаем курсы валют
        city_salary_data = defaultdict(list)

        vacancies = Vacancy.objects.all()
        for vacancy in vacancies:
            if not vacancy.area_name:
                continue

            rate = self.get_currency_rate(vacancy.salary_currency, vacancy.published_at)
            salary_values = [v for v in [vacancy.salary_from, vacancy.salary_to] if v]
            if salary_values:
                avg_salary = sum(salary_values) / len(salary_values)
                salary_in_rub = avg_salary * rate
                city_salary_data[vacancy.area_name].append(salary_in_rub)

        avg_salary_by_city = [
            {"area_name": city, "avg_salary": round(sum(salaries) / len(salaries), 2)}
            for city, salaries in city_salary_data.items()
            if salaries
        ]

        return avg_salary_by_city

    def get_vacancy_share_by_city(self):
        """
        Возвращает долю вакансий по городам (в порядке убывания).
        """
        total_vacancies = Vacancy.objects.count()
        if total_vacancies == 0:
            return []

        vacancies = Vacancy.objects.values("area_name").annotate(
            count=Count("id"),
            share=(Count("id") * 100.0 / total_vacancies)
        ).order_by("-share")[:10]

        return [
            {
                "area_name": vacancy["area_name"],
                "share": round(vacancy["share"], 2)
            }
            for vacancy in vacancies
        ]

    def get_top_skills(self, year: int):
        """
        Возвращает ТОП-20 навыков за указанный год.
        """
        from collections import Counter

        skills = Vacancy.objects.filter(
            published_at__year=year
        ).values_list("key_skills", flat=True)

        skill_counter = Counter()
        for skill_set in skills:
            if skill_set:
                skill_counter.update(skill_set.split(", "))

        return skill_counter.most_common(20)
