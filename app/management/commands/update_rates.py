import asyncio
import logging
from datetime import datetime
from xml.etree import ElementTree as ET
import httpx
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from ...models import Vacancy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CBRApi:
    def __init__(self):
        self.base_url = "https://www.cbr.ru/scripts/XML_daily.asp"

    async def get_currency_rate(self, currency: str, date: datetime):
        url = f"{self.base_url}?date_req={date.strftime('%d/%m/%Y')}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    xml_text = response.text
                    return self._parse_currency_rate(xml_text, currency)
        except Exception as e:
            logger.error(f"Error fetching currency rate: {e}")
        return None

    def _parse_currency_rate(self, xml: str, currency: str):
        root = ET.fromstring(xml)
        for valute in root.findall("Valute"):
            char_code = valute.find("CharCode").text
            if char_code == currency:
                value = valute.find("Value").text.replace(",", ".")
                nominal = int(valute.find("Nominal").text)
                return float(value) / nominal
        return None


async def update_exchange_rate(vacancy_id, api, date, request_count):
    vacancy = await sync_to_async(Vacancy.objects.get)(id=vacancy_id)

    if not vacancy.salary_currency:
        logger.info(f"Skipping vacancy {vacancy.name} with empty currency")
        return False

    if vacancy.salary_currency == 'RUR':
        vacancy.exchange_rate_to_rub = 1.0
        await sync_to_async(vacancy.save)()
        logger.info(f"Set rate for {vacancy.name} to 1 (RUR)")
        return True
    else:
        rate = await api.get_currency_rate(vacancy.salary_currency, date)
        request_count += 1

        if request_count % 10 == 0:
            logger.info(f"Requests made so far: {request_count}")

        if rate is not None:
            vacancy.exchange_rate_to_rub = rate
            await sync_to_async(vacancy.save)()
            logger.info(f"Updated {vacancy.name} with rate {rate}")
            return True
        else:
            logger.warning(f"Failed to fetch rate for {vacancy.salary_currency}")

    return False


async def update_exchange_rates():
    api = CBRApi()
    date = datetime.now()

    await sync_to_async(Vacancy.objects.filter(salary_currency='RUR').update)(exchange_rate_to_rub=1)

    vacancies = await sync_to_async(lambda: list(Vacancy.objects.filter(
        salary_currency__isnull=False).exclude(salary_currency='RUR')))()

    total_requests = 0
    successful_updates = 0

    tasks = []

    for vacancy in vacancies:
        tasks.append(update_exchange_rate(vacancy.id, api, date, total_requests))

    for i in range(0, len(tasks), 10):
        results = await asyncio.gather(*tasks[i:i + 10])
        successful_updates += sum(results)
        await asyncio.sleep(0.1)

    logger.info(f"Total requests made: {total_requests}")
    logger.info(f"Successful currency updates: {successful_updates}")


class Command(BaseCommand):
    help = 'Update currency exchange rates from CBR'

    def handle(self, *args, **kwargs):
        asyncio.run(update_exchange_rates())