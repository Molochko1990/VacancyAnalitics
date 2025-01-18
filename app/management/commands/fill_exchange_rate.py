from django.core.management.base import BaseCommand
from django.db import transaction
from .get_all_currency import get_all_currency
from app.models import Vacancy
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update exchange rates for vacancies'

    def handle(self, *args, **kwargs):
        logger.info("Запуск команды обновления курсов валют для вакансий.")

        # Получить курсы валют
        currency_rates = get_all_currency()

        # Начать транзакцию для безопасного обновления
        with transaction.atomic():
            vacancies = Vacancy.objects.exclude(salary_currency__in=['RUR', '']).all()
            logger.info(f"Найдено {len(vacancies)} вакансий для обновления.")

            for vacancy in vacancies:
                published_date = vacancy.published_at
                year_month = f"{published_date.year}-{published_date.month:02d}"
                currency = vacancy.salary_currency

                if year_month in currency_rates and currency in currency_rates[year_month]:
                    exchange_rate = currency_rates[year_month][currency]
                    vacancy.exchange_rate_to_rub = exchange_rate
                    logger.debug(f"Обновление курса {currency} для вакансии ID {vacancy.id}: {exchange_rate}")
                else:
                    logger.warning(f"Курс для валюты {currency} на {year_month} не найден для вакансии ID {vacancy.id}")

                vacancy.save()

        logger.info("Обновление курсов валют для вакансий завершено.")
