import requests

class CBRApi:
    def __init__(self):
        self.base_url = "https://www.cbr.ru/scripts/XML_daily.asp"
        self.cache = {}
        self.request_count = 0

    def _get_month_start(self, date):
        return date.replace(day=1)

    def get_currency_rate(self, currency, date):
        """
        Получить курс валюты на указанное число.
        """
        self.request_count += 1
        print(f"Запрос №{self.request_count}: курс валюты {currency} за {date}")
        # Логика вызова API
        if currency == "RUR":
            return 1

        date_key = self._get_month_start(date)
        cache_key = (currency, date_key)

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Запрос курса на указанную дату
        params = {"date_req": date_key.strftime("%d/%m/%Y")}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        # Парсинг ответа
        rate = self._parse_currency_rate(response.text, currency)
        if rate:
            self.cache[cache_key] = rate
        return rate

    def _parse_currency_rate(self, xml, currency):
        from xml.etree import ElementTree as ET

        root = ET.fromstring(xml)
        for valute in root.findall("Valute"):
            char_code = valute.find("CharCode").text
            if char_code == currency:
                value = valute.find("Value").text.replace(",", ".")
                nominal = int(valute.find("Nominal").text)
                return float(value) / nominal
        return None
