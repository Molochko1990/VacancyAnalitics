from django.shortcuts import render
from .services.vacancy_service import VacancyService


def index(request):
    return render(request, 'index.html')


def statistics_view(request):
    service = VacancyService()

    salary_dynamics = service.get_avg_salary_by_year()
    salary_chart_path = service.save_salary_dynamics_chart(salary_dynamics)

    vacancy_dynamics = service.get_vacancy_count_by_year()
    vacancy_chart_path = service.save_vacancy_count_chart(vacancy_dynamics)

    salary_by_city = service.get_salary_by_city()
    salary_by_city_chart_path = service.save_salary_by_city_chart(salary_by_city)

    vacancy_share_by_city = service.get_vacancy_share_by_city()
    vacancy_share_by_city_chart_path = service.save_vacancy_share_by_city_chart(vacancy_share_by_city)

    top_skills = service.get_top_skills(2024)

    context = {
        'salary_dynamics': salary_dynamics,
        'salary_chart_path': salary_chart_path,
        'vacancy_dynamics': vacancy_dynamics,
        'vacancy_chart_path': vacancy_chart_path,
        'salary_by_city': salary_by_city,
        'salary_by_city_chart_path': salary_by_city_chart_path,
        'vacancy_share_by_city': vacancy_share_by_city,
        'vacancy_share_by_city_chart_path': vacancy_share_by_city_chart_path,
        'top_skills': top_skills,
        'year': 2024,
    }

    return render(request, 'statistics.html', context)

