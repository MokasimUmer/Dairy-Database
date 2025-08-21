import sqlite3
from datetime import date

def record_milk_collection(source_type, supplier_id=None, quantity_liters=0, fat_content=None, collected_by_employee=None):
    conn = sqlite3.connect('dairy.db')
    cursor = conn.cursor()
    today = date.today()
    cursor.execute('''
    INSERT INTO MilkCollection (date, source_type, supplier_id, quantity_liters, fat_content, collected_by_employee)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (today, source_type, supplier_id, quantity_liters, fat_content, collected_by_employee))
    conn.commit()
    conn.close()
    print("Milk collection recorded.")

# Usage: record_milk_collection('farm', quantity_liters=1000, collected_by_employee=1)

def perform_separation(milk_collection_id, milk_used_liters, cream_liters, skimmed_milk_liters, whole_milk_liters):
    conn = sqlite3.connect('dairy.db')
    cursor = conn.cursor()
    today = date.today()
    cursor.execute('''
    INSERT INTO MilkSeparation (date, milk_collection_id, milk_used_liters, cream_liters, skimmed_milk_liters, whole_milk_liters)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (today, milk_collection_id, milk_used_liters, cream_liters, skimmed_milk_liters, whole_milk_liters))
    # Optionally update stock for cream/skim/whole here
    conn.commit()
    conn.close()
    print("Milk separation recorded.")

def record_production(product_id, milk_used_liters, produced_by_employee):
  conn = sqlite3.connect('dairy.db')
  cursor = conn.cursor()
  # Fetch ratio
  cursor.execute('SELECT ratio_to_milk, unit FROM Products WHERE id = ?', (product_id,))
  ratio, unit = cursor.fetchone()
  quantity_produced = milk_used_liters / ratio if ratio else 0
  today = date.today()
  cursor.execute('''
  INSERT INTO Production (date, product_id, milk_used_liters, quantity_produced, produced_by_employee)
  VALUES (?, ?, ?, ?, ?)
  ''', (today, product_id, milk_used_liters, quantity_produced, produced_by_employee))
  # Update stock
  cursor.execute('''
  UPDATE Stock SET current_quantity = current_quantity + ?, last_updated = ?
  WHERE product_id = ?
  ''', (quantity_produced, today, product_id))
  conn.commit()
  conn.close()
  print(f"Produced {quantity_produced} {unit} of product.")
def record_sale(customer_id, shop_id, product_id, quantity, total_price):
  conn = sqlite3.connect('dairy.db')
  cursor = conn.cursor()
  today = date.today()
  # Check stock
  cursor.execute('SELECT current_quantity FROM Stock WHERE product_id = ?', (product_id,))
  current = cursor.fetchone()[0]
  if current < quantity:
      print("Insufficient stock!")
      return
  cursor.execute('''
  INSERT INTO Sales (date, customer_id, shop_id, product_id, quantity, total_price)
  VALUES (?, ?, ?, ?, ?, ?)
  ''', (today, customer_id, shop_id, product_id, quantity, total_price))
  # Reduce stock
  cursor.execute('''
  UPDATE Stock SET current_quantity = current_quantity - ?, last_updated = ?
  WHERE product_id = ?
  ''', (quantity, today, product_id))
  conn.commit()
  conn.close()
  print("Sale recorded.")