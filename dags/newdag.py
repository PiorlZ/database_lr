from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2
import subprocess
import sys

# Настройки подключения к базе данных
DB_SETTINGS = {
    "dbname": "souvenirs_db",
    "user": "user",
    "password": "password",
    "host": "db",
    "port": 5432,
}

# Функция для подключения к базе данных
def get_db_connection():
    return psycopg2.connect(**DB_SETTINGS)


# Функция для установки необходимых зависимостей
def install_dependencies():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

def load_data_():
    install_dependencies()
    import pandas as pd
    import random

    # Путь к файлу Excel
    data_file = "/opt/airflow/dags/data.xlsx"
    data = pd.read_excel(data_file)

    # Заменяем NaN на корректные значения
    fill_values = {
        'color': "",  # Пустая строка для текстовых столбцов
        'material': "",
        'applicMetod': "",  # Приведено в соответствие с колонкой
        'weight': 0,  # Ноль для числовых столбцов
        'qtypics': 0,
        'picssize': "",
        'categoryid': 0,  # Приведено в соответствие с колонкой
        'vendorcode': ""
    }
    data = data.fillna(value=fill_values)

    # Преобразуем данные в стандартные типы Python
    data = data.astype({
        'weight': float,
        'qtypics': int,
        'categoryid': int  # Приведено в соответствие с колонкой
    })

    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    # 1. Уникальные провайдеры
    unique_vendors = data['vendorcode'].dropna().unique()
    for vendor in unique_vendors:
        cursor.execute("""
            INSERT INTO providers (name, email, contactperson, comments)
            VALUES (%s, NULL, NULL, NULL) ON CONFLICT DO NOTHING
        """, (str(vendor),))

    # 2. Уникальные цвета
    unique_colors = data['color'].dropna().unique()
    for color in unique_colors:
        cursor.execute("""
            INSERT INTO color (name) VALUES (%s) ON CONFLICT DO NOTHING
        """, (str(color),))

    # 3. Уникальные материалы
    unique_materials = data['material'].dropna().unique()
    for material in unique_materials:
        cursor.execute("""
            INSERT INTO souvenirmaterials (name) VALUES (%s) ON CONFLICT DO NOTHING
        """, (str(material),))

    # 4. Уникальные методы нанесения
    unique_methods = data['applicMetod'].dropna().unique()  # Приведено в соответствие с колонкой
    for method in unique_methods:
        cursor.execute("""
            INSERT INTO applicationmethods (name) VALUES (%s) ON CONFLICT DO NOTHING
        """, (str(method),))

    # 5. Категории
    unique_categories = data['categoryid'].dropna().unique()
    for category_id in unique_categories:
        cursor.execute("""
            INSERT INTO souvenirscategories (id, idParent, name)
            VALUES (%s, NULL, %s) ON CONFLICT DO NOTHING
        """, (int(category_id), f"Category {category_id}"))

    # 6. Сувениры
    for _, row in data.iterrows():
        cursor.execute("""
            INSERT INTO souvenirs (
                shortname, name, description, rating, idcategory, idcolor, idmaterial, idapplicMethod,
                size, weight, dealerPrice, price
            )
            SELECT %s, %s, %s, %s,
                   (SELECT id FROM souvenirscategories WHERE id = %s),
                   (SELECT id FROM color WHERE name = %s),
                   (SELECT id FROM souvenirmaterials WHERE name = %s),
                   (SELECT id FROM applicationmethods WHERE name = %s),
                   %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM souvenirs WHERE shortname = %s
            )
        """, (
            str(row['shortname']), str(row['name']), str(row['description']), float(row['rating']),
            int(row['categoryid']), str(row['color']), str(row['material']), str(row['applicMetod']),
            str(row['prodsize']), float(row['weight']), float(row['dealerPrice']), float(row['price']),
            str(row['shortname'])
        ))

    # 7. Закупки
    for i in range(10):  # Создаем 10 закупок с рандомизированными данными
        cursor.execute("""
            INSERT INTO souvenirprocurements (idprovider, data, idstatus)
            VALUES (
                (SELECT id FROM providers ORDER BY RANDOM() LIMIT 1),
                NOW(),
                NULL
            )
            ON CONFLICT DO NOTHING
        """)

    # 8. Детали закупок
    for i in range(20):  # 20 случайных закупок
        cursor.execute("""
            INSERT INTO procurementsouvenirs (idsouvenir, idprocurement, amount, price)
            VALUES (
                (SELECT id FROM souvenirs ORDER BY RANDOM() LIMIT 1),
                (SELECT id FROM souvenirprocurements ORDER BY RANDOM() LIMIT 1),
                %s, %s
            )
            ON CONFLICT DO NOTHING
        """, (random.randint(1, 10), random.uniform(10.0, 100.0)))

    # 9. Заполнение склада
    for i in range(15):  # 15 случайных записей о хранении
        cursor.execute("""
            INSERT INTO souvenirstores (idprocurement, idsouvenir, amount, comments)
            VALUES (
                (SELECT id FROM souvenirprocurements ORDER BY RANDOM() LIMIT 1),
                (SELECT id FROM souvenirs ORDER BY RANDOM() LIMIT 1),
                %s,
                'Автоматически добавлено'
            )
            ON CONFLICT DO NOTHING
        """, (random.randint(1, 20),))

    db_conn.commit()
    cursor.close()
    db_conn.close()



# Определение DAG
with DAG(
    dag_id="dadadadadada",
    schedule_interval=None,
    start_date=datetime(2024, 12, 1),
    catchup=False,
) as dag:

    load_data_ = PythonOperator(
        task_id="load_data_",
        python_callable=load_data_,
    )

    # Зависимость задач
    load_data_
