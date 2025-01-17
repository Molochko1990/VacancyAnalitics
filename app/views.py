from django.shortcuts import render
from .services.vacancy_service import VacancyService
from asgiref.sync import sync_to_async
from .models import Vacancy
import asyncio
import pandas as pd


def index(request):
    return render(request, 'index.html')


def statistics_view(request):
    service = VacancyService()

    # При условии, что данные уже загружены воркером Celery.
    salary_dynamics = service.get_avg_salary_by_year()
    vacancy_dynamics = service.get_vacancy_count_by_year()
    salary_by_city = service.get_salary_by_city()
    vacancy_share_by_city = service.get_vacancy_share_by_city()
    top_skills = service.get_top_skills(2024)

    context = {
        'salary_dynamics': salary_dynamics,
        'vacancy_dynamics': vacancy_dynamics,
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
        'top_skills': top_skills,
        'year': 2024,
    }

    return render(request, 'statistics.html', context)

