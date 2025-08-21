from flask import Flask, render_template_string, request, redirect, url_for, flash
import sqlite3
from datetime import date

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super_secret_key'  # For flash messages

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('dairy.db')
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    return conn

# Helper to execute queries
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# Base template with Bootstrap and Navbar
base_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dairy Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { margin-top: 20px; }
        .navbar-brand { font-weight: bold; }
        .flash-message { margin-bottom: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Dairy Management System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Reports</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('view_stock') }}">Stock Levels</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('view_sales') }}">Recent Sales</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('view_customers') }}">Top Customers</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('view_employees') }}">Employee Productivity</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('view_shops') }}">Shop Performance</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Data Management</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('list_suppliers') }}">Suppliers</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_milk_collections') }}">Milk Collections</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_separations') }}">Milk Separations</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_products') }}">Products</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_productions') }}">Productions</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_employees') }}">Employees</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_shops') }}">Shops</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_expenses') }}">Expenses</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_salaries') }}">Salaries</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_customers') }}">Customers</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('list_sales') }}">Sales</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container">
        {% for message in get_flashed_messages() %}
            <div class="alert alert-info flash-message">{{ message }}</div>
        {% endfor %}
        {{ content|safe }}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Home route
@app.route('/')
def index():
    content = '''
    <h1 class="mt-4">Welcome to Dairy Management System</h1>
    <p>Use the navigation bar above to view reports or manage data.</p>
    '''
    return render_template_string(base_template, content=content)

# --- Reports ---
@app.route('/stock')
def view_stock():
    stocks = execute_query('''
    SELECT p.product_name, s.current_quantity, p.unit, s.last_updated
    FROM Stock s JOIN Products p ON s.product_id = p.id
    ORDER BY s.current_quantity ASC
    ''', fetchall=True)
    content = '<h2 class="mt-4">Stock Levels</h2>'
    if not stocks:
        content += '<p>No stock data available.</p>'
    else:
        content += '''
        <table class="table table-striped table-hover">
            <thead><tr><th>Product</th><th>Quantity</th><th>Unit</th><th>Last Updated</th></tr></thead>
            <tbody>
        '''
        for stock in stocks:
            content += f'''
            <tr>
                <td>{stock['product_name']}</td>
                <td>{stock['current_quantity']}</td>
                <td>{stock['unit']}</td>
                <td>{stock['last_updated']}</td>
            </tr>
            '''
        content += '</tbody></table>'
    return render_template_string(base_template, content=content)

@app.route('/sales')
def view_sales():
    sales = execute_query('''
    SELECT s.date, c.name AS customer, sh.name AS shop, p.product_name, s.quantity, s.total_price
    FROM Sales s JOIN Customers c ON s.customer_id = c.id
    JOIN Shops sh ON s.shop_id = sh.id JOIN Products p ON s.product_id = p.id
    ORDER BY s.date DESC LIMIT 10
    ''', fetchall=True)
    content = '<h2 class="mt-4">Recent Sales (Last 10)</h2>'
    if not sales:
        content += '<p>No sales data available.</p>'
    else:
        content += '''
        <table class="table table-striped table-hover">
            <thead><tr><th>Date</th><th>Customer</th><th>Shop</th><th>Product</th><th>Quantity</th><th>Price</th></tr></thead>
            <tbody>
        '''
        for sale in sales:
            content += f'''
            <tr>
                <td>{sale['date']}</td>
                <td>{sale['customer']}</td>
                <td>{sale['shop']}</td>
                <td>{sale['product_name']}</td>
                <td>{sale['quantity']}</td>
                <td>{sale['total_price']}</td>
            </tr>
            '''
        content += '</tbody></table>'
    return render_template_string(base_template, content=content)

@app.route('/customers')
def view_customers():
    customers = execute_query('''
    SELECT c.name, SUM(s.quantity) AS total_volume, SUM(s.total_price) AS total_spent
    FROM Sales s JOIN Customers c ON s.customer_id = c.id
    GROUP BY c.id ORDER BY total_volume DESC LIMIT 5
    ''', fetchall=True)
    content = '<h2 class="mt-4">Top Customers by Volume</h2>'
    if not customers:
        content += '<p>No customer data available.</p>'
    else:
        content += '''
        <table class="table table-striped table-hover">
            <thead><tr><th>Customer</th><th>Total Volume</th><th>Total Spent</th></tr></thead>
            <tbody>
        '''
        for customer in customers:
            content += f'''
            <tr>
                <td>{customer['name']}</td>
                <td>{customer['total_volume']}</td>
                <td>{customer['total_spent']}</td>
            </tr>
            '''
        content += '</tbody></table>'
    return render_template_string(base_template, content=content)

@app.route('/employees')
def view_employees():
    employees = execute_query('''
    SELECT e.name, SUM(p.quantity_produced) AS total_produced
    FROM Production p JOIN Employees e ON p.produced_by_employee = e.id
    GROUP BY e.id ORDER BY total_produced DESC
    ''', fetchall=True)
    content = '<h2 class="mt-4">Employee Productivity</h2>'
    if not employees:
        content += '<p>No production data available.</p>'
    else:
        content += '''
        <table class="table table-striped table-hover">
            <thead><tr><th>Employee</th><th>Total Produced</th></tr></thead>
            <tbody>
        '''
        for employee in employees:
            content += f'''
            <tr>
                <td>{employee['name']}</td>
                <td>{employee['total_produced']}</td>
            </tr>
            '''
        content += '</tbody></table>'
    return render_template_string(base_template, content=content)

@app.route('/shops')
def view_shops():
    shops = execute_query('''
    SELECT sh.name, SUM(s.total_price) AS total_sales,
           (SELECT SUM(e.amount) FROM Expenses e WHERE e.shop_id = sh.id) AS total_expenses,
           SUM(s.total_price) - (SELECT SUM(e.amount) FROM Expenses e WHERE e.shop_id = sh.id) AS net_profit
    FROM Sales s JOIN Shops sh ON s.shop_id = sh.id
    GROUP BY sh.id
    ''', fetchall=True)
    content = '<h2 class="mt-4">Shop Performance</h2>'
    if not shops:
        content += '<p>No shop data available.</p>'
    else:
        content += '''
        <table class="table table-striped table-hover">
            <thead><tr><th>Shop</th><th>Total Sales</th><th>Total Expenses</th><th>Net Profit</th></tr></thead>
            <tbody>
        '''
        for shop in shops:
            total_expenses = shop['total_expenses'] if shop['total_expenses'] is not None else 0
            net_profit = shop['net_profit'] if shop['net_profit'] is not None else 0
            content += f'''
            <tr>
                <td>{shop['name']}</td>
                <td>{shop['total_sales']}</td>
                <td>{total_expenses}</td>
                <td>{net_profit}</td>
            </tr>
            '''
        content += '</tbody></table>'
    return render_template_string(base_template, content=content)

# --- Data Management ---

# Suppliers
@app.route('/suppliers', methods=['GET'])
def list_suppliers():
    suppliers = execute_query("SELECT * FROM Suppliers", fetchall=True)
    content = '<h2 class="mt-4">Manage Suppliers</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Name</th><th>Contact</th><th>Address</th><th>Actions</th></tr></thead><tbody>'
    for sup in suppliers:
        content += f'<tr><td>{sup["id"]}</td><td>{sup["name"]}</td><td>{sup["contact"]}</td><td>{sup["address"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_supplier/{sup["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_supplier/{sup["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    content += '''
    <h3>Add Supplier</h3>
    <form method="POST" action="/add_supplier" class="row g-3">
        <div class="col-md-4"><label class="form-label">Name</label><input name="name" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Contact</label><input name="contact" class="form-control"></div>
        <div class="col-md-4"><label class="form-label">Address</label><input name="address" class="form-control"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    name = request.form['name']
    contact = request.form['contact']
    address = request.form['address']
    execute_query("INSERT INTO Suppliers (name, contact, address) VALUES (?, ?, ?)", (name, contact, address))
    flash('Supplier added successfully')
    return redirect(url_for('list_suppliers'))

@app.route('/edit_supplier/<int:id>', methods=['GET', 'POST'])
def edit_supplier(id):
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        execute_query("UPDATE Suppliers SET name=?, contact=?, address=? WHERE id=?", (name, contact, address, id))
        flash('Supplier updated successfully')
        return redirect(url_for('list_suppliers'))
    supplier = execute_query("SELECT * FROM Suppliers WHERE id=?", (id,), fetchone=True)
    content = f'''
    <h2 class="mt-4">Edit Supplier</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Name</label><input name="name" class="form-control" value="{supplier['name']}" required></div>
        <div class="col-md-4"><label class="form-label">Contact</label><input name="contact" class="form-control" value="{supplier['contact']}"></div>
        <div class="col-md-4"><label class="form-label">Address</label><input name="address" class="form-control" value="{supplier['address']}"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_supplier/<int:id>')
def delete_supplier(id):
    execute_query("DELETE FROM Suppliers WHERE id=?", (id,))
    flash('Supplier deleted successfully')
    return redirect(url_for('list_suppliers'))

# Milk Collections
@app.route('/milk_collections', methods=['GET'])
def list_milk_collections():
    collections = execute_query("SELECT * FROM MilkCollection", fetchall=True)
    content = '<h2 class="mt-4">Manage Milk Collections</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Date</th><th>Source Type</th><th>Supplier ID</th><th>Quantity (L)</th><th>Fat Content</th><th>Collected By</th><th>Actions</th></tr></thead><tbody>'
    for col in collections:
        content += f'<tr><td>{col["id"]}</td><td>{col["date"]}</td><td>{col["source_type"]}</td><td>{col["supplier_id"]}</td><td>{col["quantity_liters"]}</td><td>{col["fat_content"]}</td><td>{col["collected_by_employee"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_milk_collection/{col["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_milk_collection/{col["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    employees = execute_query("SELECT id, name FROM Employees", fetchall=True)
    suppliers = execute_query("SELECT id, name FROM Suppliers", fetchall=True)
    emp_options = ''.join([f'<option value="{emp["id"]}">{emp["name"]}</option>' for emp in employees])
    sup_options = ''.join([f'<option value="{sup["id"]}">{sup["name"]}</option>' for sup in suppliers])
    content += f'''
    <h3>Add Milk Collection</h3>
    <form method="POST" action="/add_milk_collection" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{date.today()}" required></div>
        <div class="col-md-4"><label class="form-label">Source Type</label><select name="source_type" class="form-select"><option value="farm">Farm</option><option value="supplier">Supplier</option></select></div>
        <div class="col-md-4"><label class="form-label">Supplier</label><select name="supplier_id" class="form-select"><option value="">None</option>{sup_options}</select></div>
        <div class="col-md-4"><label class="form-label">Quantity (L)</label><input name="quantity_liters" type="number" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Fat Content</label><input name="fat_content" type="number" step="0.1" class="form-control"></div>
        <div class="col-md-4"><label class="form-label">Collected By</label><select name="collected_by_employee" class="form-select">{emp_options}</select></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_milk_collection', methods=['POST'])
def add_milk_collection():
    date_val = request.form['date']
    source_type = request.form['source_type']
    supplier_id = request.form['supplier_id'] or None
    quantity_liters = request.form['quantity_liters']
    fat_content = request.form['fat_content'] or None
    collected_by = request.form['collected_by_employee']
    execute_query("INSERT INTO MilkCollection (date, source_type, supplier_id, quantity_liters, fat_content, collected_by_employee) VALUES (?, ?, ?, ?, ?, ?)",
                  (date_val, source_type, supplier_id, quantity_liters, fat_content, collected_by))
    flash('Milk collection recorded')
    return redirect(url_for('list_milk_collections'))

@app.route('/edit_milk_collection/<int:id>', methods=['GET', 'POST'])
def edit_milk_collection(id):
    if request.method == 'POST':
        date_val = request.form['date']
        source_type = request.form['source_type']
        supplier_id = request.form['supplier_id'] or None
        quantity_liters = request.form['quantity_liters']
        fat_content = request.form['fat_content'] or None
        collected_by = request.form['collected_by_employee']
        execute_query("UPDATE MilkCollection SET date=?, source_type=?, supplier_id=?, quantity_liters=?, fat_content=?, collected_by_employee=? WHERE id=?",
                      (date_val, source_type, supplier_id, quantity_liters, fat_content, collected_by, id))
        flash('Milk collection updated')
        return redirect(url_for('list_milk_collections'))
    collection = execute_query("SELECT * FROM MilkCollection WHERE id=?", (id,), fetchone=True)
    employees = execute_query("SELECT id, name FROM Employees", fetchall=True)
    suppliers = execute_query("SELECT id, name FROM Suppliers", fetchall=True)
    emp_options = ''.join([f'<option value="{emp["id"]}" {"selected" if emp["id"] == collection["collected_by_employee"] else ""}>{emp["name"]}</option>' for emp in employees])
    sup_options = ''.join([f'<option value="{sup["id"]}" {"selected" if sup["id"] == collection["supplier_id"] else ""}>{sup["name"]}</option>' for sup in suppliers])
    content = f'''
    <h2 class="mt-4">Edit Milk Collection</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{collection["date"]}" required></div>
        <div class="col-md-4"><label class="form-label">Source Type</label><select name="source_type" class="form-select"><option value="farm" {"selected" if collection["source_type"] == "farm" else ""}>Farm</option><option value="supplier" {"selected" if collection["source_type"] == "supplier" else ""}>Supplier</option></select></div>
        <div class="col-md-4"><label class="form-label">Supplier</label><select name="supplier_id" class="form-select"><option value="">None</option>{sup_options}</select></div>
        <div class="col-md-4"><label class="form-label">Quantity (L)</label><input name="quantity_liters" type="number" class="form-control" value="{collection["quantity_liters"]}" required></div>
        <div class="col-md-4"><label class="form-label">Fat Content</label><input name="fat_content" type="number" step="0.1" class="form-control" value="{collection["fat_content"]}"></div>
        <div class="col-md-4"><label class="form-label">Collected By</label><select name="collected_by_employee" class="form-select">{emp_options}</select></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_milk_collection/<int:id>')
def delete_milk_collection(id):
    execute_query("DELETE FROM MilkCollection WHERE id=?", (id,))
    flash('Milk collection deleted')
    return redirect(url_for('list_milk_collections'))

# Milk Separations
@app.route('/separations', methods=['GET'])
def list_separations():
    separations = execute_query("SELECT * FROM MilkSeparation", fetchall=True)
    content = '<h2 class="mt-4">Manage Milk Separations</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Date</th><th>Milk Collection ID</th><th>Milk Used (L)</th><th>Cream (L)</th><th>Skimmed (L)</th><th>Whole (L)</th><th>Actions</th></tr></thead><tbody>'
    for sep in separations:
        content += f'<tr><td>{sep["id"]}</td><td>{sep["date"]}</td><td>{sep["milk_collection_id"]}</td><td>{sep["milk_used_liters"]}</td><td>{sep["cream_liters"]}</td><td>{sep["skimmed_milk_liters"]}</td><td>{sep["whole_milk_liters"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_separation/{sep["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_separation/{sep["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    collections = execute_query("SELECT id FROM MilkCollection", fetchall=True)
    col_options = ''.join([f'<option value="{col["id"]}">{col["id"]}</option>' for col in collections])
    content += f'''
    <h3>Add Milk Separation</h3>
    <form method="POST" action="/add_separation" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{date.today()}" required></div>
        <div class="col-md-4"><label class="form-label">Milk Collection ID</label><select name="milk_collection_id" class="form-select">{col_options}</select></div>
        <div class="col-md-4"><label class="form-label">Milk Used (L)</label><input name="milk_used_liters" type="number" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Cream (L)</label><input name="cream_liters" type="number" class="form-control"></div>
        <div class="col-md-4"><label class="form-label">Skimmed (L)</label><input name="skimmed_milk_liters" type="number" class="form-control"></div>
        <div class="col-md-4"><label class="form-label">Whole (L)</label><input name="whole_milk_liters" type="number" class="form-control"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_separation', methods=['POST'])
def add_separation():
    date_val = request.form['date']
    milk_collection_id = request.form['milk_collection_id']
    milk_used = request.form['milk_used_liters']
    cream = request.form['cream_liters']
    skimmed = request.form['skimmed_milk_liters']
    whole = request.form['whole_milk_liters']
    execute_query("INSERT INTO MilkSeparation (date, milk_collection_id, milk_used_liters, cream_liters, skimmed_milk_liters, whole_milk_liters) VALUES (?, ?, ?, ?, ?, ?)",
                  (date_val, milk_collection_id, milk_used, cream, skimmed, whole))
    flash('Milk separation recorded')
    return redirect(url_for('list_separations'))

@app.route('/edit_separation/<int:id>', methods=['GET', 'POST'])
def edit_separation(id):
    if request.method == 'POST':
        date_val = request.form['date']
        milk_collection_id = request.form['milk_collection_id']
        milk_used = request.form['milk_used_liters']
        cream = request.form['cream_liters']
        skimmed = request.form['skimmed_milk_liters']
        whole = request.form['whole_milk_liters']
        execute_query("UPDATE MilkSeparation SET date=?, milk_collection_id=?, milk_used_liters=?, cream_liters=?, skimmed_milk_liters=?, whole_milk_liters=? WHERE id=?",
                      (date_val, milk_collection_id, milk_used, cream, skimmed, whole, id))
        flash('Milk separation updated')
        return redirect(url_for('list_separations'))
    separation = execute_query("SELECT * FROM MilkSeparation WHERE id=?", (id,), fetchone=True)
    collections = execute_query("SELECT id FROM MilkCollection", fetchall=True)
    col_options = ''.join([f'<option value="{col["id"]}" {"selected" if col["id"] == separation["milk_collection_id"] else ""}>{col["id"]}</option>' for col in collections])
    content = f'''
    <h2 class="mt-4">Edit Milk Separation</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{separation["date"]}" required></div>
        <div class="col-md-4"><label class="form-label">Milk Collection ID</label><select name="milk_collection_id" class="form-select">{col_options}</select></div>
        <div class="col-md-4"><label class="form-label">Milk Used (L)</label><input name="milk_used_liters" type="number" class="form-control" value="{separation["milk_used_liters"]}" required></div>
        <div class="col-md-4"><label class="form-label">Cream (L)</label><input name="cream_liters" type="number" class="form-control" value="{separation["cream_liters"]}"></div>
        <div class="col-md-4"><label class="form-label">Skimmed (L)</label><input name="skimmed_milk_liters" type="number" class="form-control" value="{separation["skimmed_milk_liters"]}"></div>
        <div class="col-md-4"><label class="form-label">Whole (L)</label><input name="whole_milk_liters" type="number" class="form-control" value="{separation["whole_milk_liters"]}"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_separation/<int:id>')
def delete_separation(id):
    execute_query("DELETE FROM MilkSeparation WHERE id=?", (id,))
    flash('Milk separation deleted')
    return redirect(url_for('list_separations'))

# Products
@app.route('/products', methods=['GET'])
def list_products():
    products = execute_query("SELECT * FROM Products", fetchall=True)
    content = '<h2 class="mt-4">Manage Products</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Name</th><th>Category</th><th>Ratio to Milk</th><th>Unit</th><th>Actions</th></tr></thead><tbody>'
    for prod in products:
        content += f'<tr><td>{prod["id"]}</td><td>{prod["product_name"]}</td><td>{prod["category"]}</td><td>{prod["ratio_to_milk"]}</td><td>{prod["unit"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_product/{prod["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_product/{prod["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    content += '''
    <h3>Add Product</h3>
    <form method="POST" action="/add_product" class="row g-3">
        <div class="col-md-3"><label class="form-label">Name</label><input name="product_name" class="form-control" required></div>
        <div class="col-md-3"><label class="form-label">Category</label><input name="category" class="form-control"></div>
        <div class="col-md-3"><label class="form-label">Ratio to Milk</label><input name="ratio_to_milk" type="number" step="0.1" class="form-control"></div>
        <div class="col-md-3"><label class="form-label">Unit</label><input name="unit" class="form-control"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    category = request.form['category']
    ratio_to_milk = request.form['ratio_to_milk'] or None
    unit = request.form['unit']
    cursor = get_db_connection().cursor()
    cursor.execute("INSERT INTO Products (product_name, category, ratio_to_milk, unit) VALUES (?, ?, ?, ?)",
                   (product_name, category, ratio_to_milk, unit))
    product_id = cursor.lastrowid
    cursor.execute("INSERT INTO Stock (product_id, current_quantity, last_updated) VALUES (?, 0, ?)",
                   (product_id, date.today()))
    cursor.connection.commit()
    cursor.connection.close()
    flash('Product added and stock initialized')
    return redirect(url_for('list_products'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if request.method == 'POST':
        product_name = request.form['product_name']
        category = request.form['category']
        ratio_to_milk = request.form['ratio_to_milk'] or None
        unit = request.form['unit']
        execute_query("UPDATE Products SET product_name=?, category=?, ratio_to_milk=?, unit=? WHERE id=?",
                      (product_name, category, ratio_to_milk, unit, id))
        flash('Product updated')
        return redirect(url_for('list_products'))
    product = execute_query("SELECT * FROM Products WHERE id=?", (id,), fetchone=True)
    content = f'''
    <h2 class="mt-4">Edit Product</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-3"><label class="form-label">Name</label><input name="product_name" class="form-control" value="{product["product_name"]}" required></div>
        <div class="col-md-3"><label class="form-label">Category</label><input name="category" class="form-control" value="{product["category"]}"></div>
        <div class="col-md-3"><label class="form-label">Ratio to Milk</label><input name="ratio_to_milk" type="number" step="0.1" class="form-control" value="{product["ratio_to_milk"]}"></div>
        <div class="col-md-3"><label class="form-label">Unit</label><input name="unit" class="form-control" value="{product["unit"]}"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    execute_query("DELETE FROM Stock WHERE product_id=?", (id,))
    execute_query("DELETE FROM Products WHERE id=?", (id,))
    flash('Product deleted')
    return redirect(url_for('list_products'))

# Productions
@app.route('/productions', methods=['GET'])
def list_productions():
    productions = execute_query("SELECT p.id, p.date, pr.product_name, p.milk_used_liters, p.quantity_produced, e.name AS employee FROM Production p JOIN Products pr ON p.product_id = pr.id JOIN Employees e ON p.produced_by_employee = e.id", fetchall=True)
    content = '<h2 class="mt-4">Manage Productions</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Date</th><th>Product</th><th>Milk Used (L)</th><th>Quantity Produced</th><th>Produced By</th><th>Actions</th></tr></thead><tbody>'
    for prod in productions:
        content += f'<tr><td>{prod["id"]}</td><td>{prod["date"]}</td><td>{prod["product_name"]}</td><td>{prod["milk_used_liters"]}</td><td>{prod["quantity_produced"]}</td><td>{prod["employee"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_production/{prod["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_production/{prod["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    products = execute_query("SELECT id, product_name FROM Products", fetchall=True)
    employees = execute_query("SELECT id, name FROM Employees", fetchall=True)
    prod_options = ''.join([f'<option value="{p["id"]}">{p["product_name"]}</option>' for p in products])
    emp_options = ''.join([f'<option value="{e["id"]}">{e["name"]}</option>' for e in employees])
    content += f'''
    <h3>Add Production</h3>
    <form method="POST" action="/add_production" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{date.today()}" required></div>
        <div class="col-md-4"><label class="form-label">Product</label><select name="product_id" class="form-select">{prod_options}</select></div>
        <div class="col-md-4"><label class="form-label">Milk Used (L)</label><input name="milk_used_liters" type="number" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Produced By</label><select name="produced_by_employee" class="form-select">{emp_options}</select></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_production', methods=['POST'])
def add_production():
    date_val = request.form['date']
    product_id = request.form['product_id']
    milk_used = float(request.form['milk_used_liters'])
    produced_by = request.form['produced_by_employee']
    ratio_row = execute_query("SELECT ratio_to_milk, unit FROM Products WHERE id=?", (product_id,), fetchone=True)
    ratio = float(ratio_row['ratio_to_milk']) if ratio_row and ratio_row['ratio_to_milk'] else 1.0
    quantity_produced = milk_used / ratio
    execute_query("INSERT INTO Production (date, product_id, milk_used_liters, quantity_produced, produced_by_employee) VALUES (?, ?, ?, ?, ?)",
                  (date_val, product_id, milk_used, quantity_produced, produced_by))
    execute_query("UPDATE Stock SET current_quantity = current_quantity + ?, last_updated = ? WHERE product_id = ?",
                  (quantity_produced, date_val, product_id))
    flash('Production recorded and stock updated')
    return redirect(url_for('list_productions'))

@app.route('/edit_production/<int:id>', methods=['GET', 'POST'])
def edit_production(id):
    if request.method == 'POST':
        date_val = request.form['date']
        product_id = request.form['product_id']
        milk_used = float(request.form['milk_used_liters'])
        produced_by = request.form['produced_by_employee']
        old_prod = execute_query("SELECT product_id, quantity_produced FROM Production WHERE id=?", (id,), fetchone=True)
        ratio_row = execute_query("SELECT ratio_to_milk FROM Products WHERE id=?", (product_id,), fetchone=True)
        ratio = float(ratio_row['ratio_to_milk']) if ratio_row and ratio_row['ratio_to_milk'] else 1.0
        quantity_produced = milk_used / ratio
        execute_query("UPDATE Production SET date=?, product_id=?, milk_used_liters=?, quantity_produced=?, produced_by_employee=? WHERE id=?",
                      (date_val, product_id, milk_used, quantity_produced, produced_by, id))
        if old_prod['product_id'] == int(product_id):
            quantity_diff = quantity_produced - old_prod['quantity_produced']
            execute_query("UPDATE Stock SET current_quantity = current_quantity + ?, last_updated = ? WHERE product_id = ?",
                          (quantity_diff, date_val, product_id))
        else:
            execute_query("UPDATE Stock SET current_quantity = current_quantity - ?, last_updated = ? WHERE product_id = ?",
                          (old_prod['quantity_produced'], date_val, old_prod['product_id']))
            execute_query("UPDATE Stock SET current_quantity = current_quantity + ?, last_updated = ? WHERE product_id = ?",
                          (quantity_produced, date_val, product_id))
        flash('Production updated and stock adjusted')
        return redirect(url_for('list_productions'))
    production = execute_query("SELECT * FROM Production WHERE id=?", (id,), fetchone=True)
    products = execute_query("SELECT id, product_name FROM Products", fetchall=True)
    employees = execute_query("SELECT id, name FROM Employees", fetchall=True)
    prod_options = ''.join([f'<option value="{p["id"]}" {"selected" if p["id"] == production["product_id"] else ""}>{p["product_name"]}</option>' for p in products])
    emp_options = ''.join([f'<option value="{e["id"]}" {"selected" if e["id"] == production["produced_by_employee"] else ""}>{e["name"]}</option>' for e in employees])
    content = f'''
    <h2 class="mt-4">Edit Production</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{production["date"]}" required></div>
        <div class="col-md-4"><label class="form-label">Product</label><select name="product_id" class="form-select">{prod_options}</select></div>
        <div class="col-md-4"><label class="form-label">Milk Used (L)</label><input name="milk_used_liters" type="number" class="form-control" value="{production["milk_used_liters"]}" required></div>
        <div class="col-md-4"><label class="form-label">Produced By</label><select name="produced_by_employee" class="form-select">{emp_options}</select></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_production/<int:id>')
def delete_production(id):
    prod = execute_query("SELECT product_id, quantity_produced FROM Production WHERE id=?", (id,), fetchone=True)
    execute_query("UPDATE Stock SET current_quantity = current_quantity - ?, last_updated = ? WHERE product_id = ?",
                  (prod['quantity_produced'], date.today(), prod['product_id']))
    execute_query("DELETE FROM Production WHERE id=?", (id,))
    flash('Production deleted and stock updated')
    return redirect(url_for('list_productions'))

# Employees
@app.route('/employees/list', methods=['GET'])
def list_employees():
    employees = execute_query("SELECT * FROM Employees", fetchall=True)
    content = '<h2 class="mt-4">Manage Employees</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Position</th><th>Shop ID</th><th>Monthly Salary</th><th>Actions</th></tr></thead><tbody>'
    for emp in employees:
        content += f'<tr><td>{emp["id"]}</td><td>{emp["name"]}</td><td>{emp["role"]}</td><td>{emp["position"]}</td><td>{emp["shop_id"]}</td><td>{emp["monthly_salary"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_employee/{emp["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_employee/{emp["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    shops = execute_query("SELECT id, name FROM Shops", fetchall=True)
    shop_options = ''.join([f'<option value="{s["id"]}">{s["name"]}</option>' for s in shops])
    content += f'''
    <h3>Add Employee</h3>
    <form method="POST" action="/add_employee" class="row g-3">
        <div class="col-md-3"><label class="form-label">Name</label><input name="name" class="form-control" required></div>
        <div class="col-md-3"><label class="form-label">Role</label><input name="role" class="form-control"></div>
        <div class="col-md-3"><label class="form-label">Position</label><input name="position" class="form-control"></div>
        <div class="col-md-3"><label class="form-label">Shop</label><select name="shop_id" class="form-select"><option value="">None</option>{shop_options}</select></div>
        <div class="col-md-3"><label class="form-label">Monthly Salary</label><input name="monthly_salary" type="number" class="form-control"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    role = request.form['role']
    position = request.form['position']
    shop_id = request.form['shop_id'] or None
    monthly_salary = request.form['monthly_salary'] or None
    execute_query("INSERT INTO Employees (name, role, position, shop_id, monthly_salary) VALUES (?, ?, ?, ?, ?)",
                  (name, role, position, shop_id, monthly_salary))
    flash('Employee added')
    return redirect(url_for('list_employees'))

@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        position = request.form['position']
        shop_id = request.form['shop_id'] or None
        monthly_salary = request.form['monthly_salary'] or None
        execute_query("UPDATE Employees SET name=?, role=?, position=?, shop_id=?, monthly_salary=? WHERE id=?",
                      (name, role, position, shop_id, monthly_salary, id))
        flash('Employee updated')
        return redirect(url_for('list_employees'))
    employee = execute_query("SELECT * FROM Employees WHERE id=?", (id,), fetchone=True)
    shops = execute_query("SELECT id, name FROM Shops", fetchall=True)
    shop_options = ''.join([f'<option value="{s["id"]}" {"selected" if s["id"] == employee["shop_id"] else ""}>{s["name"]}</option>' for s in shops])
    content = f'''
    <h2 class="mt-4">Edit Employee</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-3"><label class="form-label">Name</label><input name="name" class="form-control" value="{employee["name"]}" required></div>
        <div class="col-md-3"><label class="form-label">Role</label><input name="role" class="form-control" value="{employee["role"]}"></div>
        <div class="col-md-3"><label class="form-label">Position</label><input name="position" class="form-control" value="{employee["position"]}"></div>
        <div class="col-md-3"><label class="form-label">Shop</label><select name="shop_id" class="form-select"><option value="">None</option>{shop_options}</select></div>
        <div class="col-md-3"><label class="form-label">Monthly Salary</label><input name="monthly_salary" type="number" class="form-control" value="{employee["monthly_salary"]}"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    execute_query("DELETE FROM Employees WHERE id=?", (id,))
    flash('Employee deleted')
    return redirect(url_for('list_employees'))

# Shops
@app.route('/shops/list', methods=['GET'])
def list_shops():
    shops = execute_query("SELECT * FROM Shops", fetchall=True)
    content = '<h2 class="mt-4">Manage Shops</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Location</th><th>Actions</th></tr></thead><tbody>'
    for shop in shops:
        content += f'<tr><td>{shop["id"]}</td><td>{shop["name"]}</td><td>{shop["type"]}</td><td>{shop["location"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_shop/{shop["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_shop/{shop["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    content += '''
    <h3>Add Shop</h3>
    <form method="POST" action="/add_shop" class="row g-3">
        <div class="col-md-4"><label class="form-label">Name</label><input name="name" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Type</label><select name="type" class="form-select"><option value="general">General</option><option value="milk_focused">Milk Focused</option></select></div>
        <div class="col-md-4"><label class="form-label">Location</label><input name="location" class="form-control"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_shop', methods=['POST'])
def add_shop():
    name = request.form['name']
    type_ = request.form['type']
    location = request.form['location']
    execute_query("INSERT INTO Shops (name, type, location) VALUES (?, ?, ?)", (name, type_, location))
    flash('Shop added')
    return redirect(url_for('list_shops'))

@app.route('/edit_shop/<int:id>', methods=['GET', 'POST'])
def edit_shop(id):
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        location = request.form['location']
        execute_query("UPDATE Shops SET name=?, type=?, location=? WHERE id=?", (name, type_, location, id))
        flash('Shop updated')
        return redirect(url_for('list_shops'))
    shop = execute_query("SELECT * FROM Shops WHERE id=?", (id,), fetchone=True)
    content = f'''
    <h2 class="mt-4">Edit Shop</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Name</label><input name="name" class="form-control" value="{shop["name"]}" required></div>
        <div class="col-md-4"><label class="form-label">Type</label><select name="type" class="form-select"><option value="general" {"selected" if shop["type"] == "general" else ""}>General</option><option value="milk_focused" {"selected" if shop["type"] == "milk_focused" else ""}>Milk Focused</option></select></div>
        <div class="col-md-4"><label class="form-label">Location</label><input name="location" class="form-control" value="{shop["location"]}"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_shop/<int:id>')
def delete_shop(id):
    execute_query("DELETE FROM Shops WHERE id=?", (id,))
    flash('Shop deleted')
    return redirect(url_for('list_shops'))

# Expenses
@app.route('/expenses', methods=['GET'])
def list_expenses():
    expenses = execute_query("SELECT e.id, e.date, s.name AS shop, e.description, e.amount FROM Expenses e JOIN Shops s ON e.shop_id = s.id", fetchall=True)
    content = '<h2 class="mt-4">Manage Expenses</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Date</th><th>Shop</th><th>Description</th><th>Amount</th><th>Actions</th></tr></thead><tbody>'
    for exp in expenses:
        content += f'<tr><td>{exp["id"]}</td><td>{exp["date"]}</td><td>{exp["shop"]}</td><td>{exp["description"]}</td><td>{exp["amount"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_expense/{exp["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_expense/{exp["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    shops = execute_query("SELECT id, name FROM Shops", fetchall=True)
    shop_options = ''.join([f'<option value="{s["id"]}">{s["name"]}</option>' for s in shops])
    content += f'''
    <h3>Add Expense</h3>
    <form method="POST" action="/add_expense" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{date.today()}" required></div>
        <div class="col-md-4"><label class="form-label">Shop</label><select name="shop_id" class="form-select">{shop_options}</select></div>
        <div class="col-md-4"><label class="form-label">Description</label><input name="description" class="form-control"></div>
        <div class="col-md-4"><label class="form-label">Amount</label><input name="amount" type="number" step="0.01" class="form-control" required></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    date_val = request.form['date']
    shop_id = request.form['shop_id']
    description = request.form['description']
    amount = request.form['amount']
    execute_query("INSERT INTO Expenses (date, shop_id, description, amount) VALUES (?, ?, ?, ?)",
                  (date_val, shop_id, description, amount))
    flash('Expense recorded')
    return redirect(url_for('list_expenses'))

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    if request.method == 'POST':
        date_val = request.form['date']
        shop_id = request.form['shop_id']
        description = request.form['description']
        amount = request.form['amount']
        execute_query("UPDATE Expenses SET date=?, shop_id=?, description=?, amount=? WHERE id=?",
                      (date_val, shop_id, description, amount, id))
        flash('Expense updated')
        return redirect(url_for('list_expenses'))
    expense = execute_query("SELECT * FROM Expenses WHERE id=?", (id,), fetchone=True)
    shops = execute_query("SELECT id, name FROM Shops", fetchall=True)
    shop_options = ''.join([f'<option value="{s["id"]}" {"selected" if s["id"] == expense["shop_id"] else ""}>{s["name"]}</option>' for s in shops])
    content = f'''
    <h2 class="mt-4">Edit Expense</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{expense["date"]}" required></div>
        <div class="col-md-4"><label class="form-label">Shop</label><select name="shop_id" class="form-select">{shop_options}</select></div>
        <div class="col-md-4"><label class="form-label">Description</label><input name="description" class="form-control" value="{expense["description"]}"></div>
        <div class="col-md-4"><label class="form-label">Amount</label><input name="amount" type="number" step="0.01" class="form-control" value="{expense["amount"]}" required></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    execute_query("DELETE FROM Expenses WHERE id=?", (id,))
    flash('Expense deleted')
    return redirect(url_for('list_expenses'))

# Salaries
@app.route('/salaries', methods=['GET'])
def list_salaries():
    salaries = execute_query("SELECT s.id, s.date, e.name AS employee, s.amount_paid FROM Salaries s JOIN Employees e ON s.employee_id = e.id", fetchall=True)
    content = '<h2 class="mt-4">Manage Salaries</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Date</th><th>Employee</th><th>Amount Paid</th><th>Actions</th></tr></thead><tbody>'
    for sal in salaries:
        content += f'<tr><td>{sal["id"]}</td><td>{sal["date"]}</td><td>{sal["employee"]}</td><td>{sal["amount_paid"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_salary/{sal["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_salary/{sal["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    employees = execute_query("SELECT id, name FROM Employees", fetchall=True)
    emp_options = ''.join([f'<option value="{e["id"]}">{e["name"]}</option>' for e in employees])
    content += f'''
    <h3>Add Salary</h3>
    <form method="POST" action="/add_salary" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{date.today()}" required></div>
        <div class="col-md-4"><label class="form-label">Employee</label><select name="employee_id" class="form-select">{emp_options}</select></div>
        <div class="col-md-4"><label class="form-label">Amount Paid</label><input name="amount_paid" type="number" step="0.01" class="form-control" required></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_salary', methods=['POST'])
def add_salary():
    date_val = request.form['date']
    employee_id = request.form['employee_id']
    amount_paid = request.form['amount_paid']
    execute_query("INSERT INTO Salaries (date, employee_id, amount_paid) VALUES (?, ?, ?)",
                  (date_val, employee_id, amount_paid))
    flash('Salary recorded')
    return redirect(url_for('list_salaries'))

@app.route('/edit_salary/<int:id>', methods=['GET', 'POST'])
def edit_salary(id):
    if request.method == 'POST':
        date_val = request.form['date']
        employee_id = request.form['employee_id']
        amount_paid = request.form['amount_paid']
        execute_query("UPDATE Salaries SET date=?, employee_id=?, amount_paid=? WHERE id=?",
                      (date_val, employee_id, amount_paid, id))
        flash('Salary updated')
        return redirect(url_for('list_salaries'))
    salary = execute_query("SELECT * FROM Salaries WHERE id=?", (id,), fetchone=True)
    employees = execute_query("SELECT id, name FROM Employees", fetchall=True)
    emp_options = ''.join([f'<option value="{e["id"]}" {"selected" if e["id"] == salary["employee_id"] else ""}>{e["name"]}</option>' for e in employees])
    content = f'''
    <h2 class="mt-4">Edit Salary</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{salary["date"]}" required></div>
        <div class="col-md-4"><label class="form-label">Employee</label><select name="employee_id" class="form-select">{emp_options}</select></div>
        <div class="col-md-4"><label class="form-label">Amount Paid</label><input name="amount_paid" type="number" step="0.01" class="form-control" value="{salary["amount_paid"]}" required></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_salary/<int:id>')
def delete_salary(id):
    execute_query("DELETE FROM Salaries WHERE id=?", (id,))
    flash('Salary deleted')
    return redirect(url_for('list_salaries'))

# Customers
@app.route('/customers/list', methods=['GET'])
def list_customers():
    customers = execute_query("SELECT * FROM Customers", fetchall=True)
    content = '<h2 class="mt-4">Manage Customers</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Name</th><th>Contact</th><th>Address</th><th>Actions</th></tr></thead><tbody>'
    for cust in customers:
        content += f'<tr><td>{cust["id"]}</td><td>{cust["name"]}</td><td>{cust["contact"]}</td><td>{cust["address"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_customer/{cust["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_customer/{cust["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    content += '''
    <h3>Add Customer</h3>
    <form method="POST" action="/add_customer" class="row g-3">
        <div class="col-md-4"><label class="form-label">Name</label><input name="name" class="form-control" required></div>
        <div class="col-md-4"><label class="form-label">Contact</label><input name="contact" class="form-control"></div>
        <div class="col-md-4"><label class="form-label">Address</label><input name="address" class="form-control"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form['name']
    contact = request.form['contact']
    address = request.form['address']
    execute_query("INSERT INTO Customers (name, contact, address) VALUES (?, ?, ?)", (name, contact, address))
    flash('Customer added')
    return redirect(url_for('list_customers'))

@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        execute_query("UPDATE Customers SET name=?, contact=?, address=? WHERE id=?", (name, contact, address, id))
        flash('Customer updated')
        return redirect(url_for('list_customers'))
    customer = execute_query("SELECT * FROM Customers WHERE id=?", (id,), fetchone=True)
    content = f'''
    <h2 class="mt-4">Edit Customer</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-4"><label class="form-label">Name</label><input name="name" class="form-control" value="{customer["name"]}" required></div>
        <div class="col-md-4"><label class="form-label">Contact</label><input name="contact" class="form-control" value="{customer["contact"]}"></div>
        <div class="col-md-4"><label class="form-label">Address</label><input name="address" class="form-control" value="{customer["address"]}"></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    execute_query("DELETE FROM Customers WHERE id=?", (id,))
    flash('Customer deleted')
    return redirect(url_for('list_customers'))

# Sales
@app.route('/sales/list', methods=['GET'])
def list_sales():
    sales = execute_query("SELECT s.id, s.date, c.name AS customer, sh.name AS shop, p.product_name, s.quantity, s.total_price FROM Sales s JOIN Customers c ON s.customer_id = c.id JOIN Shops sh ON s.shop_id = sh.id JOIN Products p ON s.product_id = p.id", fetchall=True)
    content = '<h2 class="mt-4">Manage Sales</h2><table class="table table-striped table-hover"><thead><tr><th>ID</th><th>Date</th><th>Customer</th><th>Shop</th><th>Product</th><th>Quantity</th><th>Total Price</th><th>Actions</th></tr></thead><tbody>'
    for sale in sales:
        content += f'<tr><td>{sale["id"]}</td><td>{sale["date"]}</td><td>{sale["customer"]}</td><td>{sale["shop"]}</td><td>{sale["product_name"]}</td><td>{sale["quantity"]}</td><td>{sale["total_price"]}</td><td><a class="btn btn-sm btn-primary" href="/edit_sale/{sale["id"]}">Edit</a> <a class="btn btn-sm btn-danger" href="/delete_sale/{sale["id"]}">Delete</a></td></tr>'
    content += '</tbody></table>'
    customers = execute_query("SELECT id, name FROM Customers", fetchall=True)
    shops = execute_query("SELECT id, name FROM Shops", fetchall=True)
    products = execute_query("SELECT id, product_name FROM Products", fetchall=True)
    cust_options = ''.join([f'<option value="{c["id"]}">{c["name"]}</option>' for c in customers])
    shop_options = ''.join([f'<option value="{s["id"]}">{s["name"]}</option>' for s in shops])
    prod_options = ''.join([f'<option value="{p["id"]}">{p["product_name"]}</option>' for p in products])
    content += f'''
    <h3>Add Sale</h3>
    <form method="POST" action="/add_sale" class="row g-3">
        <div class="col-md-3"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{date.today()}" required></div>
        <div class="col-md-3"><label class="form-label">Customer</label><select name="customer_id" class="form-select">{cust_options}</select></div>
        <div class="col-md-3"><label class="form-label">Shop</label><select name="shop_id" class="form-select">{shop_options}</select></div>
        <div class="col-md-3"><label class="form-label">Product</label><select name="product_id" class="form-select">{prod_options}</select></div>
        <div class="col-md-3"><label class="form-label">Quantity</label><input name="quantity" type="number" step="0.01" class="form-control" required></div>
        <div class="col-md-3"><label class="form-label">Total Price</label><input name="total_price" type="number" step="0.01" class="form-control" required></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Add</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)

@app.route('/add_sale', methods=['POST'])
def add_sale():
    date_val = request.form['date']
    customer_id = request.form['customer_id']
    shop_id = request.form['shop_id']
    product_id = request.form['product_id']
    quantity = float(request.form['quantity'])
    total_price = float(request.form['total_price'])
    stock_row = execute_query("SELECT current_quantity FROM Stock WHERE product_id=?", (product_id,), fetchone=True)
    current = stock_row['current_quantity'] if stock_row else 0
    if current < quantity:
        flash('Insufficient stock!')
        return redirect(url_for('list_sales'))
    execute_query("INSERT INTO Sales (date, customer_id, shop_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                  (date_val, customer_id, shop_id, product_id, quantity, total_price))
    execute_query("UPDATE Stock SET current_quantity = current_quantity - ?, last_updated = ? WHERE product_id = ?",
                  (quantity, date_val, product_id))
    flash('Sale recorded and stock updated')
    return redirect(url_for('list_sales'))

@app.route('/edit_sale/<int:id>', methods=['GET', 'POST'])
def edit_sale(id):
    if request.method == 'POST':
        date_val = request.form['date']
        customer_id = request.form['customer_id']
        shop_id = request.form['shop_id']
        product_id = request.form['product_id']
        quantity = float(request.form['quantity'])
        total_price = float(request.form['total_price'])
        old_sale = execute_query("SELECT product_id, quantity FROM Sales WHERE id=?", (id,), fetchone=True)
        stock_row = execute_query("SELECT current_quantity FROM Stock WHERE product_id=?", (product_id,), fetchone=True)
        current = stock_row['current_quantity'] if stock_row else 0
        quantity_diff = quantity - old_sale['quantity']
        if current < quantity_diff:
            flash('Insufficient stock for update!')
            return redirect(url_for('list_sales'))
        execute_query("UPDATE Sales SET date=?, customer_id=?, shop_id=?, product_id=?, quantity=?, total_price=? WHERE id=?",
                      (date_val, customer_id, shop_id, product_id, quantity, total_price, id))
        if old_sale['product_id'] == int(product_id):
            execute_query("UPDATE Stock SET current_quantity = current_quantity - ?, last_updated = ? WHERE product_id = ?",
                          (quantity_diff, date_val, product_id))
        else:
            execute_query("UPDATE Stock SET current_quantity = current_quantity + ?, last_updated = ? WHERE product_id = ?",
                          (old_sale['quantity'], date_val, old_sale['product_id']))
            execute_query("UPDATE Stock SET current_quantity = current_quantity - ?, last_updated = ? WHERE product_id = ?",
                          (quantity, date_val, product_id))
        flash('Sale updated and stock adjusted')
        return redirect(url_for('list_sales'))
    sale = execute_query("SELECT * FROM Sales WHERE id=?", (id,), fetchone=True)
    customers = execute_query("SELECT id, name FROM Customers", fetchall=True)
    shops = execute_query("SELECT id, name FROM Shops", fetchall=True)
    products = execute_query("SELECT id, product_name FROM Products", fetchall=True)
    cust_options = ''.join([f'<option value="{c["id"]}" {"selected" if c["id"] == sale["customer_id"] else ""}>{c["name"]}</option>' for c in customers])
    shop_options = ''.join([f'<option value="{s["id"]}" {"selected" if s["id"] == sale["shop_id"] else ""}>{s["name"]}</option>' for s in shops])
    prod_options = ''.join([f'<option value="{p["id"]}" {"selected" if p["id"] == sale["product_id"] else ""}>{p["product_name"]}</option>' for p in products])
    content = f'''
    <h2 class="mt-4">Edit Sale</h2>
    <form method="POST" class="row g-3">
        <div class="col-md-3"><label class="form-label">Date</label><input name="date" type="date" class="form-control" value="{sale["date"]}" required></div>
        <div class="col-md-3"><label class="form-label">Customer</label><select name="customer_id" class="form-select">{cust_options}</select></div>
        <div class="col-md-3"><label class="form-label">Shop</label><select name="shop_id" class="form-select">{shop_options}</select></div>
        <div class="col-md-3"><label class="form-label">Product</label><select name="product_id" class="form-select">{prod_options}</select></div>
        <div class="col-md-3"><label class="form-label">Quantity</label><input name="quantity" type="number" step="0.01" class="form-control" value="{sale["quantity"]}" required></div>
        <div class="col-md-3"><label class="form-label">Total Price</label><input name="total_price" type="number" step="0.01" class="form-control" value="{sale["total_price"]}" required></div>
        <div class="col-12"><button type="submit" class="btn btn-primary">Update</button></div>
    </form>
    '''
    return render_template_string(base_template, content=content)
@app.route('/delete_sale/<int:id>')
def delete_sale(id):
    sale = execute_query("SELECT product_id, quantity FROM Sales WHERE id=?", (id,), fetchone=True)
    execute_query("UPDATE Stock SET current_quantity = current_quantity + ?, last_updated = ? WHERE product_id = ?",
                  (sale['quantity'], date.today(), sale['product_id']))
    execute_query("DELETE FROM Sales WHERE id=?", (id,))
    flash('Sale deleted and stock updated')
    return redirect(url_for('list_sales'))
if __name__ == '__main__':
    app.run(debug=True)