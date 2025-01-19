import psycopg2


connection = psycopg2.connect(
    dbname='vacancies',
    user='postgres',
    password='masha123',
    host='localhost',
    port='5432'
)

cursor = connection.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS vacancies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    key_skills TEXT,
    salary_from INTEGER,
    salary_to INTEGER,
    salary_currency VARCHAR(10),
    area_name VARCHAR(255),
    published_at TIMESTAMP
);
'''
cursor.execute(create_table_query)
connection.commit()

print("Table 'vacancies' created successfully")

cursor.close()
connection.close()

