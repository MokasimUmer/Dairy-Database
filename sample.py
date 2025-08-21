import sqlite3

conn = sqlite3.connect('dairy.db')
cursor = conn.cursor()

# Insert sample products
cursor.execute("INSERT INTO Products (product_name, category, ratio_to_milk, unit) VALUES ('Cheese', 'Dairy Product', 10.0, 'kg')")
cursor.execute("INSERT INTO Products (product_name, category, ratio_to_milk, unit) VALUES ('Boiled Milk', 'Raw Material', 1.0, 'liters')")
cursor.execute("INSERT INTO Shops (name, type, location) VALUES ('General Dairy Shop', 'general', 'Downtown')")
cursor.execute("INSERT INTO Shops (name, type, location) VALUES ('Milk Shop', 'milk_focused', 'Suburb')")
cursor.execute("INSERT INTO Customers (name, contact, address) VALUES ('John Doe', '1234567890', '123 Main St')")
cursor.execute("INSERT INTO Employees (name, role, position, monthly_salary) VALUES ('Alice', 'Processor', 'Lead', 2000)")
cursor.execute("INSERT INTO Stock (product_id, current_quantity, last_updated) VALUES (1, 100, '2025-08-21')")
cursor.execute("INSERT INTO Stock (product_id, current_quantity, last_updated) VALUES (2, 500, '2025-08-21')")
cursor.execute("INSERT INTO Sales (date, customer_id, shop_id, product_id, quantity, total_price) VALUES ('2025-08-21', 1, 1, 1, 10, 100)")
cursor.execute("INSERT INTO Production (date, product_id, milk_used_liters, quantity_produced, produced_by_employee) VALUES ('2025-08-21', 1, 1000, 100, 1)")
cursor.execute("INSERT INTO Expenses (date, shop_id, description, amount) VALUES ('2025-08-21', 1, 'Utilities', 200)")

conn.commit()
conn.close()
print("Sample data inserted.")