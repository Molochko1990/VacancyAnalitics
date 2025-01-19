import requests
from datetime import datetime, timedelta

BASE_URL = "https://api.hh.ru/vacancies"
SEARCH_TEXT = "Разработчик"
HEADERS = {"User-Agent": "YourDjangoApp/1.0"}


def format_salary(salary):
    """Форматирование данных о зарплате."""
    if not salary:
        return "Не указана"
    salary_from = salary.get("from")
    salary_to = salary.get("to")
    currency = salary.get("currency", "")
    if salary_from and salary_to:
        return f"{salary_from} - {salary_to} {currency}"
    elif salary_from:
        return f"От {salary_from} {currency}"
    elif salary_to:
        return f"До {salary_to} {currency}"
    return "Не указана"


def fetch_vacancies():
    """Получение списка вакансий за последние 24 часа."""
    date_from = (datetime.now() - timedelta(days=1)).isoformat()
    date_to = datetime.now().isoformat()

    params = {
        "text": SEARCH_TEXT,
        "date_from": date_from,
        "date_to": date_to,
        "per_page": 10,
        "order_by": "publication_time",
        "only_with_salary": False,
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()

    return response.json().get("items", [])


def fetch_vacancy_details(vacancy_id):
    """Получение детальной информации о вакансии."""
    url = f"{BASE_URL}/{vacancy_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    details = response.json()

    return {
        "description": details.get("description", ""),
        "skills": ", ".join(skill["name"] for skill in details.get("key_skills", [])),
    }