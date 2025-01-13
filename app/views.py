from django.shortcuts import render
from .services.vacancy_service import VacancyService
from .models import Vacancy
import pandas as pd


def index(request):
    return render(request, 'index.html')

#
# def common_statistics(request):
#     service = VacancyService()
#
#     context = {
#         "avg_salary_by_year": service.get_avg_salary_by_year(),
#         "vacancy_count_by_year": service.get_vacancy_count_by_year(),
#         "salary_by_city": service.get_salary_by_city(),
#         "top_skills": service.get_top_skills(year=2023),
#     }
#
#     return render(request, "statistics.html", context)


def statistics_view(request):
    service = VacancyService()
    salary_dynamics = service.get_avg_salary_by_year()
    vacancy_dynamics = service.get_vacancy_count_by_year()
    salary_by_city = service.get_salary_by_city()
    vacancy_share_by_city = service.get_vacancy_share_by_city()
    top_skills = service.get_top_skills(2024)  # нужный год

    context = {
        'salary_dynamics': salary_dynamics,
        'vacancy_dynamics': vacancy_dynamics,
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
        'top_skills': top_skills,
        'year': 2024,
    }

    return render(request, 'statistics.html', context)

