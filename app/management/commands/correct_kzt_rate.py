from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Vacancy
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Correct KZT exchange rates for vacancies'

    def handle(self, *args, **kwargs):
        logger.info("Запуск команды коррекции курсов KZT для вакансий.")

        correct_kzt_rate = 0.19

        with transaction.atomic():
            vacancies_kzt = Vacancy.objects.filter(salary_currency='KZT')
            logger.info(f"Найдено {vacancies_kzt.count()} вакансий с валютой KZT.")

            for vacancy in vacancies_kzt:
                vacancy.exchange_rate_to_rub = correct_kzt_rate
                vacancy.save()
                logger.debug(f"Курс KZT для вакансии ID {vacancy.id} исправлен на {correct_kzt_rate}.")

        logger.info("Коррекция курсов KZT завершена.")
