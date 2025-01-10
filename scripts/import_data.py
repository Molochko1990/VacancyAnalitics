import csv
import psycopg2
from datetime import datetime

connection = psycopg2.connect(
    dbname='vacancies',
    user='postgres',
    password='masha123',
    host='localhost',
    port='5432'
)

cursor = connection.cursor()

csv_file_path = '../data/gamedev_vacancies.csv'

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Преобразование даты в формат TIMESTAMP
        try:
            published_at = datetime.fromisoformat(row['published_at'])
        except ValueError as e:
            print(f"Error parsing date: {row['published_at']} - {e}")
            continue

        # Преобразование зарплаты в целое число
        salary_from = int(float(row['salary_from'])) if row['salary_from'] else None
        salary_to = int(float(row['salary_to'])) if row['salary_to'] else None

        cursor.execute(
            """
            INSERT INTO vacancies (name, key_skills, salary_from, salary_to, salary_currency, area_name, published_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row['name'],
                row['key_skills'],
                salary_from,
                salary_to,
                row['salary_currency'],
                row['area_name'],
                published_at
            )
        )

# Подтверждение изменений и закрытие соединения
connection.commit()
cursor.close()
connection.close()

print("Data imported successfully")