import psycopg2
from psycopg2 import sql

admin_user = 'postgres'
admin_password = 'masha123'
host = 'localhost'
port = '5432'

db_name = 'vacancies'
db_user = 'user'
db_password = 'password'

conn = None
try:
    conn = psycopg2.connect(dbname='postgres', user=admin_user, password=admin_password, host=host, port=port)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    print(f"Database '{db_name}' created successfully.")

    cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(db_user)), [db_password])
    print(f"User '{db_user}' created successfully.")

    cursor.execute(
        sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(sql.Identifier(db_name), sql.Identifier(db_user)))
    print(f"All privileges on database '{db_name}' granted to user '{db_user}'.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()

