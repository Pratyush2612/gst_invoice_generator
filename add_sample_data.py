import sqlite3
import datetime

DB_FILE = 'invoices.db'

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Customers
c.executemany('''INSERT OR IGNORE INTO customers (name, gstin, address, phone, email) VALUES (?, ?, ?, ?, ?)''', [
    ("Rahul Traders", "29AAACC1234D1Z5", "123 MG Road, Bangalore", "9876543210", "rahul@email.com"),
    ("Sharma Enterprises", "27BBBBB5678E2Z6", "45 Andheri West, Mumbai", "9123456789", "sharma@ent.com"),
    ("Verma Distributors", "33CCCC9876F3Z7", "78 Connaught Place, Delhi", "9988776655", "verma.dist@gmail.com"),
])

# Sample invoice
c.execute("SELECT id FROM customers LIMIT 1")
cust = c.fetchone()
if cust:
    cust_id = cust[0]
    invoice_no = f"INV-{datetime.date.today().strftime('%Y%m%d')}-001"
    
    c.execute("""INSERT INTO invoices (invoice_no, date, customer_id, subtotal, cgst, sgst, igst, total, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
              (invoice_no, datetime.date.today().isoformat(), cust_id, 3450, 310.5, 310.5, 0, 4071, 'Pending'))
    
    # Items
    c.executemany("""INSERT INTO invoice_items (invoice_id, description, hsn, qty, rate, amount, gst_rate)
                     VALUES (last_insert_rowid(), ?, ?, ?, ?, ?, ?)""", [
        ("Wireless Mouse", "8471", 5, 450, 2250, 18),
        ("USB Cable Pack", "8544", 10, 120, 1200, 12),
    ])
    
print("Sample data added!")
conn.commit()
conn.close()
