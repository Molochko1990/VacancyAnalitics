from django.shortcuts import render
from django.http import HttpResponseServerError
from .services.vacancy_service import VacancyService
from .services.hh_service import fetch_vacancies, fetch_vacancy_details, format_salary


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


def demand_view(request):
    service = VacancyService()
    keywords = ['game', 'unity', 'игр', 'unreal']

    salary_dynamics = service.get_avg_salary_by_year(keywords=keywords)
    salary_chart_path = service.save_salary_dynamics_chart(salary_dynamics)

    vacancy_dynamics = service.get_vacancy_count_by_year(keywords=keywords)
    vacancy_chart_path = service.save_vacancy_count_chart(vacancy_dynamics)

    context = {
        'salary_dynamics': salary_dynamics,
        'salary_chart_path': salary_chart_path,
        'vacancy_dynamics': vacancy_dynamics,
        'vacancy_chart_path': vacancy_chart_path,
    }
    return render(request, 'demand.html', context)


def geography_view(request):
    service = VacancyService()
    keywords = ['game', 'unity', 'игр', 'unreal']

    salary_by_city = service.get_salary_by_city(keywords=keywords)
    salary_by_city_chart_path = service.save_salary_by_city_chart(salary_by_city)

    vacancy_share_by_city = service.get_vacancy_share_by_city(keywords=keywords)
    vacancy_share_by_city_chart_path = service.save_vacancy_share_by_city_chart(vacancy_share_by_city)

    context = {
        'salary_by_city': salary_by_city,
        'salary_by_city_chart_path': salary_by_city_chart_path,
        'vacancy_share_by_city': vacancy_share_by_city,
        'vacancy_share_by_city_chart_path': vacancy_share_by_city_chart_path,
    }
    return render(request, 'geography.html', context)


def skills_view(request):
    service = VacancyService()
    keywords = ['game', 'unity', 'игр', 'unreal']

    year = 2024
    top_skills = service.get_top_skills(year=year, keywords=keywords)

    context = {
        'top_skills': top_skills,
        'year': year,
    }
    return render(request, 'skills.html', context)

def last_vacancies(request):
    """Отображение последних вакансий на странице."""
    try:
        vacancies = fetch_vacancies()
        results = []
        for vacancy in vacancies:
            details = fetch_vacancy_details(vacancy["id"])
            results.append({
                "title": vacancy["name"],
                "description": details["description"],
                "skills": details["skills"],
                "company": vacancy["employer"]["name"],
                "salary": format_salary(vacancy["salary"]),
                "region": vacancy["area"]["name"],
                "published_at": vacancy["published_at"],
            })
        return render(request, 'last_vacancies.html', {"vacancies": results})
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return HttpResponseServerError("Ошибка при получении данных о вакансиях")