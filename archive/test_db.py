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


get_souvenirs_by_material()
get_deliveries_in_period()
get_souvenirs_sorted_by_popularity()
get_suppliers_for_category()
alert_low_stock()