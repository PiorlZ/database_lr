from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2

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

# Функция для выполнения SQL-запроса
def execute_query(query, description):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"{description}:")
        for row in results:
            print(row)
    except Exception as e:
        print(f"Ошибка выполнения запроса {description}: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 1. Выборка сувениров по материалу
def query_souvenirs_by_material():
    query = """
    SELECT s.id, s.name, sm.name AS material
    FROM souvenirs s
    JOIN souvenirmaterials sm ON s.idmaterial = sm.id
    WHERE sm.name = 'алюминий';
    """
    execute_query(query, "Сувениры по материалу")

# 2. Выборка поставок сувениров за промежуток времени
def query_deliveries_in_timeframe():
    query = """
    SELECT sp.id AS procurement_id, sp.data AS procurement_date, ps.idsouvenir AS souvenir_id, ps.amount, ps.price
    FROM souvenirprocurements sp
    JOIN procurementsouvenirs ps ON sp.id = ps.idprocurement
    WHERE sp.data BETWEEN '2024-01-01' AND '2024-12-31';
    """
    execute_query(query, "Поставки сувениров за промежуток времени")

# 3. Выборка сувениров по категориям с сортировкой по популярности
def query_souvenirs_by_category_sorted_by_popularity():
    query = """
    SELECT s.id, s.name, s.rating, sc.name AS category_name
    FROM souvenirs s
    JOIN souvenirscategories sc ON s.idcategory = sc.id
    ORDER BY s.rating ASC;
    """
    execute_query(query, "Сувениры по категориям, отсортированные по популярности")

# 4. Выборка поставщиков по категории товара
def query_suppliers_by_category():
    query = """
    SELECT DISTINCT p.name AS provider_name
    FROM providers p
    JOIN souvenirprocurements sp ON p.id = sp.idprovider
    JOIN procurementsouvenirs ps ON sp.id = ps.idprocurement
    JOIN souvenirs s ON ps.idsouvenir = s.id
    JOIN souvenirscategories sc ON s.idcategory = sc.id
    WHERE sc.name LIKE '%Шкатулки для часов%';
    """
    execute_query(query, "Поставщики, поставляющие категорию товара")

# 5. Выборка поставок сувениров за промежуток времени, отсортированных по статусу
def query_deliveries_sorted_by_status():
    query = """
    SELECT sp.id AS procurement_id, sp.data AS procurement_date, sp.idstatus
    FROM souvenirprocurements sp
    WHERE sp.data BETWEEN '2024-01-01' AND '2024-12-31'
    ORDER BY sp.idstatus;
    """
    execute_query(query, "Поставки сувениров за промежуток времени, отсортированные по статусу")

# 6. Вывод категорий, зависящих от выбранной
def display_categories_by_selection():
    selected_category = 'Электроника'
    query = f"""
    SELECT sc.id, sc.name
    FROM souvenirscategories sc
    WHERE sc.idparent = (
        SELECT id FROM souvenirscategories WHERE name = '{selected_category}'
    );
    """
    execute_query(query, f"Категории, зависящие от выбранной: {selected_category}")

# 7. Проверка правильности занесения данных в таблицу SouvenirsCategories
def validate_souvenirs_categories():
    query = """
    SELECT id, name, idparent
    FROM souvenirscategories
    WHERE idparent IS NOT NULL AND idparent NOT IN (SELECT id FROM souvenirscategories);
    """
    execute_query(query, "Проверка правильности данных в SouvenirsCategories")

# 8. Оповещение пользователя при отсутствии поставок товаров или товаров меньше 50 шт.
def alert_on_low_stock():
    query = """
    SELECT s.id, s.name, ss.amount
    FROM souvenirs s
    LEFT JOIN souvenirstores ss ON s.id = ss.idsouvenir
    WHERE ss.amount IS NULL OR ss.amount < 50;
    """
    execute_query(query, "Оповещение: товары с отсутствующим или низким запасом")

# Определение DAG
with DAG(
    dag_id="souvenir_queries",
    schedule_interval=None,
    start_date=datetime(2024, 12, 1),
    catchup=False,
) as dag:

    task_1 = PythonOperator(
        task_id="query_souvenirs_by_material",
        python_callable=query_souvenirs_by_material,
    )

    task_2 = PythonOperator(
        task_id="query_deliveries_in_timeframe",
        python_callable=query_deliveries_in_timeframe,
    )

    task_3 = PythonOperator(
        task_id="query_souvenirs_by_category_sorted_by_popularity",
        python_callable=query_souvenirs_by_category_sorted_by_popularity,
    )

    task_4 = PythonOperator(
        task_id="query_suppliers_by_category",
        python_callable=query_suppliers_by_category,
    )

    task_5 = PythonOperator(
        task_id="query_deliveries_sorted_by_status",
        python_callable=query_deliveries_sorted_by_status,
    )

    task_6 = PythonOperator(
        task_id="display_categories_by_selection",
        python_callable=display_categories_by_selection,
    )

    task_7 = PythonOperator(
        task_id="validate_souvenirs_categories",
        python_callable=validate_souvenirs_categories,
    )

    task_8 = PythonOperator(
        task_id="alert_on_low_stock",
        python_callable=alert_on_low_stock,
    )

    # Задачи можно выполнить параллельно
    [task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8]
