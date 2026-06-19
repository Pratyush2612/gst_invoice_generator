import sqlite3
import datetime

DB_FILE = 'invoices.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Customers table
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        gstin TEXT,
        address TEXT,
        phone TEXT,
        email TEXT
    )''')
    
    # Invoices table
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        invoice_no TEXT UNIQUE,
        date TEXT,
        customer_id INTEGER,
        subtotal REAL,
        cgst REAL,
        sgst REAL,
        igst REAL,
        total REAL,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')
    
    # Invoice items
    c.execute('''CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY,
        invoice_id INTEGER,
        description TEXT,
        hsn TEXT,
        qty INTEGER,
        rate REAL,
        amount REAL,
        gst_rate REAL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id)
    )''')
    
    conn.commit()
    conn.close()

def add_customer(name, gstin='', address='', phone='', email=''):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO customers (name, gstin, address, phone, email) VALUES (?, ?, ?, ?, ?)",
              (name, gstin, address, phone, email))
    conn.commit()
    customer_id = c.lastrowid
    conn.close()
    return customer_id

def get_customers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    customers = c.fetchall()
    conn.close()
    return customers

def add_invoice(invoice_no, customer_id, items, date=None):
    if date is None:
        date = datetime.date.today().isoformat()
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Calculate totals
    subtotal = 0
    cgst_total = 0
    sgst_total = 0
    igst_total = 0
    
    for item in items:
        amount = item['qty'] * item['rate']
        gst_amount = amount * (item['gst_rate'] / 100)
        # Assume intra-state for simplicity, split CGST/SGST
        cgst = gst_amount / 2
        sgst = gst_amount / 2
        igst = 0
        if item.get('is_interstate', False):
            igst = gst_amount
            cgst = sgst = 0
        subtotal += amount
        cgst_total += cgst
        sgst_total += sgst
        igst_total += igst
        item['amount'] = amount
    
    total = subtotal + cgst_total + sgst_total + igst_total
    
    c.execute("""INSERT INTO invoices (invoice_no, date, customer_id, subtotal, cgst, sgst, igst, total, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')""",
              (invoice_no, date, customer_id, subtotal, cgst_total, sgst_total, igst_total, total))
    invoice_id = c.lastrowid
    
    for item in items:
        c.execute("""INSERT INTO invoice_items (invoice_id, description, hsn, qty, rate, amount, gst_rate)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (invoice_id, item['description'], item.get('hsn', ''), item['qty'], item['rate'], item['amount'], item['gst_rate']))
    
    conn.commit()
    conn.close()
    return invoice_id

def get_invoices():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""SELECT i.*, c.name as customer_name FROM invoices i
                 LEFT JOIN customers c ON i.customer_id = c.id""")
    invoices = c.fetchall()
    conn.close()
    return invoices

def update_payment_status(invoice_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE invoices SET status = ? WHERE id = ?", (status, invoice_id))
    conn.commit()
    conn.close()

def get_invoice_details(invoice_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    invoice = c.fetchone()
    c.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    items = c.fetchall()
    conn.close()
    return invoice, items
