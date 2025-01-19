import csv
import psycopg2
from datetime import datetime
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_import.log"),
        logging.StreamHandler()
    ]
)

logging.info("Starting the data import process.")

connection = psycopg2.connect(
    dbname='vacancies',
    user='postgres',
    password='masha123',
    host='localhost',
    port='5432'
)
cursor = connection.cursor()
logging.info("Connected to the database.")

cursor.execute("SELECT pg_get_serial_sequence('vacancies', 'id');")
sequence_name = cursor.fetchone()[0]

if sequence_name:
    cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1;")
    logging.info(f"Sequence {sequence_name} reset to start from 1.")
else:
    logging.warning("Sequence for 'id' not found.")

csv_file_path = '../data/vacancies_2024.csv'

start_time = time.time()

MAX_ROWS = 100000

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    logging.info(f"Total rows in file: {len(reader)}")

    row_count = 0

    for i, row in enumerate(reader):
        if i % 50 != 0:
            continue

        try:
            published_at = datetime.fromisoformat(row['published_at'])
            if published_at.year < 2017:
                continue
        except ValueError as e:
            logging.warning(f"Error parsing date: {row['published_at']} - {e}")
            continue

        if row_count >= MAX_ROWS:
            logging.info(f"Reached the maximum limit of {MAX_ROWS} rows. Stopping the process.")
            break

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

        row_count += 1
        if row_count % 1000 == 0:
            logging.info(f"Processed {row_count} rows.")

connection.commit()
cursor.close()
connection.close()

total_time = time.time() - start_time
logging.info(f"Data import completed. Total rows processed: {row_count}. Total time: {total_time:.2f} seconds.")
