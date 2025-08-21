import sqlite3

# Connect to SQLite database (creates dairy.db if it doesn't exist)
conn = sqlite3.connect('dairy.db')
cursor = conn.cursor()

# Create Suppliers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    address TEXT
)
''')

# Create MilkCollection table
cursor.execute('''
CREATE TABLE IF NOT EXISTS MilkCollection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    source_type TEXT NOT NULL,
    supplier_id INTEGER,
    quantity_liters REAL NOT NULL,
    fat_content REAL,
    collected_by_employee INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(id),
    FOREIGN KEY (collected_by_employee) REFERENCES Employees(id)
)
''')

# Create MilkSeparation table
cursor.execute('''
CREATE TABLE IF NOT EXISTS MilkSeparation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    milk_collection_id INTEGER NOT NULL,
    milk_used_liters REAL NOT NULL,
    cream_liters REAL,
    skimmed_milk_liters REAL,
    whole_milk_liters REAL,
    FOREIGN KEY (milk_collection_id) REFERENCES MilkCollection(id)
)
''')

# Create Products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    ratio_to_milk REAL,
    unit TEXT
)
''')

# Create Production table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    product_id INTEGER NOT NULL,
    milk_used_liters REAL NOT NULL,
    quantity_produced REAL NOT NULL,
    produced_by_employee INTEGER,
    FOREIGN KEY (product_id) REFERENCES Products(id),
    FOREIGN KEY (produced_by_employee) REFERENCES Employees(id)
)
''')

# Create Stock table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    current_quantity REAL NOT NULL,
    last_updated DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(id)
)
''')

# Create Employees table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,
    position TEXT,
    shop_id INTEGER,
    monthly_salary REAL,
    FOREIGN KEY (shop_id) REFERENCES Shops(id)
)
''')

# Create Shops table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    location TEXT
)
''')

# Create Expenses table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    shop_id INTEGER NOT NULL,
    description TEXT,
    amount REAL NOT NULL,
    FOREIGN KEY (shop_id) REFERENCES Shops(id)
)
''')

# Create Salaries table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    date DATE NOT NULL,
    amount_paid REAL NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(id)
)
''')

# Create Customers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    address TEXT
)
''')

# Create Sales table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    customer_id INTEGER NOT NULL,
    shop_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(id),
    FOREIGN KEY (shop_id) REFERENCES Shops(id),
    FOREIGN KEY (product_id) REFERENCES Products(id)
)
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully with all tables.")