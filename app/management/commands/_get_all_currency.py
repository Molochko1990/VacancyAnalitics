import requests
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_all_currency():
    logger.info("Начало сбора данных о курсах валют.")
    month = 1
    year = 2016
    all_currency = 'BYR,USD,EUR,KZT,UAH,AZN,KGS,UZS,GEL'.split(',')
    result = {}

    while True:
        if year == 2024 and month == 12:
            logger.info("Завершение цикла по месяцам и годам.")
            break
        month_str = f"{month:02d}"

        try:
            logger.debug(f"Запрос данных для 01/{month_str}/{year}.")
            response = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{month_str}/{year}')
            if response.status_code != 200:
                logger.warning(
                    f"Не удалось получить данные для 01/{month_str}/{year}. Статус ответа: {response.status_code}")
                continue

            root = ET.fromstring(response.content)
            result[f'{year}-{month_str}'] = {}

            for item in root.findall('Valute'):
                name = item.find('CharCode').text
                if name in all_currency:
                    value = float(item.find('Value').text.replace(',', '.'))
                    result[f'{year}-{month_str}'][name] = value
                    logger.debug(f"Добавлен курс {name}: {value} для {year}-{month_str}")

        except Exception as e:
            logger.error(f"Ошибка обработки данных для 01/{month_str}/{year}: {e}")
            continue

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    logger.info("Сбор данных о курсах валют завершен.")
    return result
