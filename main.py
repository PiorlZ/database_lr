import os

import pandas as pd
from sqlalchemy import create_engine, text, inspect, MetaData
import time

# Ожидание перед подключением
time.sleep(10)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine('postgresql+psycopg2://user:password@db:5432/souvenirs_db')


def execute_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_commands = file.read()

    with engine.connect() as conn:
        for statement in sql_commands.split(';'):
            if statement.strip():  # Проверка на пустые команды
                try:
                    conn.execute(text(statement))
                    print(f"Executed: {statement[:50]}...")
                except Exception as e:
                    print(f"Skipped: {statement[:50]}... - {str(e)}")


# Путь к файлу CSV
csv_file_path = 'categories.csv'  # Убедитесь, что файл сохранен с таким именем

# Загрузка данных из CSV
df = pd.read_csv(csv_file_path, encoding='utf-8')  # Убедитесь, что используется правильная кодировка

# Путь к файлу Excel
excel_path = 'data.xlsx'

df_data = pd.read_excel(excel_path)

# Получение метаданных базы данных
metadata = MetaData()
metadata.reflect(bind=engine)

# Получение списка таблиц и их колонок
inspector = inspect(engine)
db_tables = inspector.get_table_names()
table_columns = {table: [col['name'] for col in inspector.get_columns(table)] for table in db_tables}

# Идентификация совпадающих колонок
matching_columns = {}
for table, columns in table_columns.items():
    matches = set(df_data.columns).intersection(columns)
    if matches:
        matching_columns[table] = list(matches)

# Печать найденных совпадений для проверки
print("Найденные совпадающие колонки:")
for table, cols in matching_columns.items():
    print(f"Таблица: {table}, Колонки: {cols}")


def get_souvenirs_by_material(material):
    query = f"SELECT * FROM souvenirs WHERE material = '{material}';"
    return query


def get_deliveries_in_period(start_date, end_date):
    query = f"SELECT * FROM deliveries WHERE delivery_date BETWEEN '{start_date}' AND '{end_date}';"
    return query


def get_souvenirs_sorted_by_popularity():
    query = "SELECT * FROM souvenirs ORDER BY popularity ASC;"
    return query


def get_suppliers_for_category(category_id):
    query = f"SELECT * FROM suppliers WHERE category_id = {category_id};"
    return query


def alert_low_stock():
    query = "SELECT * FROM stock WHERE quantity < 50;"
    return query

time.sleep(10)
# Запуск функции с указанным файлом SQL
execute_sql_file('schema.sql')

# Импорт данных в базу данных
df.to_sql('SouvenirCategories', engine, if_exists='append', index=False)

print("Данные успешно импортированы в базу данных.")

# Загрузка данных в таблицы
for table, columns in matching_columns.items():
    df_filtered = df_data[columns]

    # Исключение полей, которые не нужно вставлять, например, автоинкрементных id
    if 'id' in df_filtered.columns:
        df_filtered = df_filtered.drop(columns=['id'])

    try:
        df_filtered.to_sql(table, engine, if_exists='append', index=False)
        print(f"Данные успешно загружены в таблицу {table}")
    except Exception as e:
        print(f"Ошибка при загрузке данных в таблицу {table}: {e}")