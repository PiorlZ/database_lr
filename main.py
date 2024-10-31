import os

import pandas as pd
from sqlalchemy import create_engine, text
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
excel_file_path = 'data.xlsx'

# Загрузка данных из Excel
xls = pd.ExcelFile(excel_file_path)

# Проверьте, какие листы доступны
print("Доступные листы:", xls.sheet_names)

# Выберите лист и загрузите данные в DataFrame
df_excel = pd.read_excel(xls, sheet_name='Sheet1')  # Замените 'Sheet1' на нужный лист

# Удаление столбца, если он существует
if 'Unnamed: 0' in df_excel.columns:
    df_excel.drop(columns=['Unnamed: 0'], inplace=True)


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

# Импорт данных в базу данных
df_excel.to_sql('souvenirs', engine, if_exists='append', index=False)

print("Данные из Excel успешно импортированы в базу данных.")