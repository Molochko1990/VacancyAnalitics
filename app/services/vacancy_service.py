import os
from decimal import Decimal, InvalidOperation
from django.db.models import Count, F
from ..models import Vacancy
from django.db.models import Q
from collections import defaultdict
import matplotlib.pyplot as plt
from django.conf import settings


class VacancyService:
    def __init__(self):
        pass

    def get_avg_salary_by_year(self):
        """
        Рассчитать среднюю зарплату по годам.
        """
        salary_data = defaultdict(list)

        vacancies = Vacancy.objects.filter(Q(salary_from__isnull=False) | Q(salary_to__isnull=False))
        for vacancy in vacancies:
            year = vacancy.published_at.year
            try:
                rate = Decimal(vacancy.exchange_rate_to_rub) if vacancy.exchange_rate_to_rub else Decimal('0')
            except InvalidOperation:
                continue

            salary_values = [v for v in [vacancy.salary_from, vacancy.salary_to] if v]
            if salary_values:
                avg_salary = sum(Decimal(v) for v in salary_values) / len(salary_values)
                salary_in_rub = avg_salary * rate
                if salary_in_rub <= 1_000_000:
                    salary_data[year].append(salary_in_rub)

        avg_salary_by_year = [
            {"year": year, "avg_salary": round(sum(salaries) / len(salaries), 2)}
            for year, salaries in salary_data.items()
            if salaries
        ]

        return avg_salary_by_year

    def save_salary_dynamics_chart(self, salary_dynamics):
        salary_dynamics = sorted(salary_dynamics, key=lambda x: x['year'])
        years = [item['year'] for item in salary_dynamics]
        salaries = [item['avg_salary'] for item in salary_dynamics]

        plt.figure(figsize=(10, 6))
        plt.plot(years, salaries, marker='o')
        plt.title('Динамика уровня зарплат по годам')
        plt.xlabel('Год')
        plt.ylabel('Средняя зарплата')
        plt.grid(True)

        chart_path = os.path.join(settings.MEDIA_ROOT, 'salary_dynamics.png')
        plt.savefig(chart_path)
        plt.close()
        return chart_path

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

    def save_vacancy_count_chart(self, vacancy_count_by_year):
        vacancy_count_by_year = sorted(vacancy_count_by_year, key=lambda x: x['year'])

        years = [item['year'] for item in vacancy_count_by_year]
        counts = [item['count'] for item in vacancy_count_by_year]

        plt.figure(figsize=(10, 6))
        plt.plot(years, counts, marker='o', linestyle='-')
        plt.title('Динамика количества вакансий по годам')
        plt.xlabel('Год')
        plt.ylabel('Количество вакансий')
        plt.grid(True)

        chart_path = os.path.join(settings.MEDIA_ROOT, 'vacancy_count.png')
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    def get_salary_by_city(self):
        """ Рассчитать среднюю зарплату по городам с учётом конвертации валют. """
        city_salary_data = defaultdict(list)
        vacancies = Vacancy.objects.filter(Q(salary_from__isnull=False) | Q(salary_to__isnull=False))

        for vacancy in vacancies:
            try:
                rate = Decimal(vacancy.exchange_rate_to_rub) if vacancy.exchange_rate_to_rub else Decimal('0')
            except InvalidOperation:
                continue

            salary_values = [v for v in [vacancy.salary_from, vacancy.salary_to] if v]

            if salary_values:
                avg_salary = sum(Decimal(v) for v in salary_values) / len(
                    salary_values)
                salary_in_rub = avg_salary * rate
                if salary_in_rub <= 1_000_000:
                    city_salary_data[vacancy.area_name].append(salary_in_rub)

        avg_salary_by_city = [
            {
                "area_name": city,
                "avg_salary": round(float(sum(salaries) / len(salaries)), 2)
            }
            for city, salaries in city_salary_data.items() if salaries
        ]
        avg_salary_by_city.sort(key=lambda x: x['avg_salary'], reverse=True)

        return avg_salary_by_city

    def save_salary_by_city_chart(self, salary_by_city):
        salary_by_city = sorted(salary_by_city, key=lambda x: x['avg_salary'], reverse=True)
        top_cities = salary_by_city[:30]

        cities = [item['area_name'] for item in top_cities]
        salaries = [item['avg_salary'] for item in top_cities]

        plt.figure(figsize=(12, 8))
        plt.barh(cities, salaries, color='skyblue')
        plt.title('Средняя зарплата по городам')
        plt.xlabel('Средняя зарплата')
        plt.ylabel('Город')
        plt.grid(axis='x', linestyle='--', linewidth=0.7)

        chart_path = os.path.join(settings.MEDIA_ROOT, 'salary_by_city.png')
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
        return chart_path

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

    def save_vacancy_share_by_city_chart(self, vacancy_share_by_city):
        cities = [item['area_name'] for item in vacancy_share_by_city]
        shares = [item['share'] for item in vacancy_share_by_city]

        plt.figure(figsize=(14, 8))
        plt.barh(cities, shares, color='lightgreen')
        plt.title('Доля вакансий по городам')
        plt.xlabel('Доля (%)')
        plt.ylabel('Город')
        plt.grid(axis='x', linestyle='--', linewidth=0.7)
        plt.gca().invert_yaxis()

        chart_path = os.path.join(settings.MEDIA_ROOT, 'vacancy_share_by_city.png')
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
        return chart_path

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
