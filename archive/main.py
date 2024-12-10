import os

import pandas as pd
from sqlalchemy import create_engine, text, inspect, MetaData
import time

# Ожидание перед подключением
time.sleep(10)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine('postgresql+psycopg2://user:password@db:5432/souvenirs_db')

# Load data from Excel and CSV
data_df = pd.read_excel('data.xlsx')  # Adjust the path if needed
categories_df = pd.read_csv('categories.csv')

# Utility function to insert data into a table
def insert_data_into_table(table_name, data):
    with engine.connect() as conn:
        for _, row in data.iterrows():
            try:
                # Dynamically create an insert statement
                insert_stmt = text(f"""
                    INSERT INTO {table_name} ({', '.join(row.index)}) 
                    VALUES ({', '.join([f':{col}' for col in row.index])})
                """)
                conn.execute(insert_stmt, **row.to_dict())
            except Exception as e:
                print(f"Error inserting data into {table_name}: {e}")

# Map columns to tables and prepare data for insertion
table_mappings = {
    'souvenirs': data_df[['url', 'shortname', 'name', 'description', 'rating', 'price']],
    'color': data_df[['color']].drop_duplicates().rename(columns={'color': 'name'}),
    'souvenircategories': categories_df[['name']].drop_duplicates(),
    # Add more mappings for other tables as needed
}

# Insert data into each table
for table, data in table_mappings.items():
    print(f"Inserting data into {table}...")
    insert_data_into_table(table, data)
    print(f"Data successfully inserted into {table}")
