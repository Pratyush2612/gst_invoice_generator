import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import db
import invoice
import datetime
import os
import sqlite3

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GST Invoice & Bill Generator")
        self.root.geometry("1000x700")
        
        db.init_db()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab 1: Customers
        self.customer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customer_tab, text="Customers")
        self.setup_customer_tab()
        
        # Tab 2: Invoices
        self.invoice_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.invoice_tab, text="Invoices")
        self.setup_invoice_tab()
        
        # Tab 3: Create New Invoice
        self.create_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_tab, text="Create Invoice")
        self.setup_create_tab()
        
        # Status bar
        self.status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add Reports menu
        self.add_reports_button()
    
    def add_reports_button(self):
        """Add Reports menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Export All Invoices to Excel", command=self.export_to_excel)
        reports_menu.add_command(label="View Summary", command=lambda: messagebox.showinfo("Summary", "Full reports feature coming soon!"))
    
    def setup_customer_tab(self):
        # Treeview for customers
        columns = ('ID', 'Name', 'GSTIN', 'Address', 'Phone', 'Email')
        self.customer_tree = ttk.Treeview(self.customer_tab, columns=columns, show='headings')
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=100)
        self.customer_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(self.customer_tab)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_customers).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add Customer", command=self.add_customer_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.edit_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_customer).pack(side=tk.LEFT, padx=5)
        
        self.load_customers()
    
    def load_customers(self):
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        customers = db.get_customers()
        for cust in customers:
            self.customer_tree.insert('', 'end', values=cust)
    
    def add_customer_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Customer")
        
        ttk.Label(win, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(win, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(win, text="GSTIN:").grid(row=1, column=0, padx=5, pady=5)
        gstin_entry = ttk.Entry(win, width=40)
        gstin_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(win, text="Address:").grid(row=2, column=0, padx=5, pady=5)
        addr_entry = ttk.Entry(win, width=40)
        addr_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(win, text="Phone:").grid(row=3, column=0, padx=5, pady=5)
        phone_entry = ttk.Entry(win, width=40)
        phone_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(win, text="Email:").grid(row=4, column=0, padx=5, pady=5)
        email_entry = ttk.Entry(win, width=40)
        email_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            db.add_customer(name, gstin_entry.get(), addr_entry.get(), phone_entry.get(), email_entry.get())
            messagebox.showinfo("Success", "Customer added")
            win.destroy()
            self.load_customers()
        
        ttk.Button(win, text="Save", command=save).grid(row=5, column=1, pady=10)
    
    def edit_customer(self):
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a customer")
            return
        cust_id = self.customer_tree.item(selected[0])['values'][0]
        messagebox.showinfo("Info", "Edit functionality can be expanded later.")
    
    def delete_customer(self):
        selected = self.customer_tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete customer?"):
            cust_id = self.customer_tree.item(selected[0])['values'][0]
            conn = sqlite3.connect(db.DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM customers WHERE id=?", (cust_id,))
            conn.commit()
            conn.close()
            self.load_customers()
    
    def setup_invoice_tab(self):
        columns = ('ID', 'Invoice No', 'Date', 'Customer', 'Subtotal', 'CGST', 'SGST', 'IGST', 'Total', 'Status')
        self.invoice_tree = ttk.Treeview(self.invoice_tab, columns=columns, show='headings')
        for col in columns:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=80)
        self.invoice_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(self.invoice_tab)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_invoices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate PDF", command=self.generate_pdf_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export to Excel", command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Status", command=self.update_status).pack(side=tk.LEFT, padx=5)
        
        self.load_invoices()
    
    def load_invoices(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        invoices = db.get_invoices()
        for inv in invoices:
            self.invoice_tree.insert('', 'end', values=inv)
    
    def generate_pdf_selected(self):
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice")
            return
        inv_id = self.invoice_tree.item(selected[0])['values'][0]
        inv, items = db.get_invoice_details(inv_id)
        customers = db.get_customers()
        customer = next((c for c in customers if c[0] == inv[3]), None)
        if customer:
            pdf_name = f"invoice_{inv[1]}.pdf"
            invoice.generate_pdf(inv, customer, items, pdf_name)
            messagebox.showinfo("Success", f"PDF generated: {pdf_name}")
            if os.path.exists(pdf_name):
                try:
                    os.startfile(pdf_name) if os.name == 'nt' else os.system(f'xdg-open {pdf_name}')
                except:
                    pass
        else:
            messagebox.showerror("Error", "Customer not found")
    
    def update_status(self):
        selected = self.invoice_tree.selection()
        if not selected:
            return
        inv_id = self.invoice_tree.item(selected[0])['values'][0]
        status = tk.simpledialog.askstring("Status", "Enter status (Paid/Pending):", initialvalue="Paid")
        if status:
            db.update_payment_status(inv_id, status)
            self.load_invoices()
            messagebox.showinfo("Success", "Status updated")

    def export_to_excel(self):
        try:
            import pandas as pd
            invoices = db.get_invoices()
            if not invoices:
                messagebox.showinfo("Info", "No invoices to export")
                return
            df = pd.DataFrame(invoices, columns=['ID', 'Invoice No', 'Date', 'Customer ID', 'Subtotal', 'CGST', 'SGST', 'IGST', 'Total', 'Status'])
            filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Success", f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def setup_create_tab(self):
        ttk.Label(self.create_tab, text="Select Customer:").pack(anchor='w', padx=10, pady=5)
        self.cust_combo = ttk.Combobox(self.create_tab, width=50)
        self.cust_combo.pack(fill='x', padx=10)
        self.refresh_customers_combo()
        
        ttk.Button(self.create_tab, text="Refresh Customers", command=self.refresh_customers_combo).pack(pady=5)
        
        items_frame = ttk.LabelFrame(self.create_tab, text="Invoice Items")
        items_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        item_columns = ('Desc', 'HSN', 'Qty', 'Rate', 'GST%', 'Amount')
        self.item_tree = ttk.Treeview(items_frame, columns=item_columns, show='headings', height=8)
        for col in item_columns:
            self.item_tree.heading(col, text=col)
            self.item_tree.column(col, width=80)
        self.item_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        add_frame = ttk.Frame(items_frame)
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="Desc:").grid(row=0, column=0)
        self.desc_entry = ttk.Entry(add_frame, width=25)
        self.desc_entry.grid(row=0, column=1)
        
        ttk.Label(add_frame, text="HSN:").grid(row=0, column=2)
        self.hsn_entry = ttk.Entry(add_frame, width=10)
        self.hsn_entry.grid(row=0, column=3)
        
        ttk.Label(add_frame, text="Qty:").grid(row=0, column=4)
        self.qty_entry = ttk.Entry(add_frame, width=8)
        self.qty_entry.grid(row=0, column=5)
        
        ttk.Label(add_frame, text="Rate:").grid(row=1, column=0)
        self.rate_entry = ttk.Entry(add_frame, width=8)
        self.rate_entry.grid(row=1, column=1)
        
        ttk.Label(add_frame, text="GST%:").grid(row=1, column=2)
        self.gst_entry = ttk.Entry(add_frame, width=8)
        self.gst_entry.grid(row=1, column=3)
        
        ttk.Button(add_frame, text="Add Item", command=self.add_item_to_list).grid(row=1, column=5, padx=5)
        
        control_frame = ttk.Frame(self.create_tab)
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text="Clear Items", command=self.clear_items).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Create & Generate PDF", command=self.create_invoice).pack(side=tk.LEFT, padx=5)
        
        self.current_items = []
    
    def refresh_customers_combo(self):
        customers = db.get_customers()
        self.cust_combo['values'] = [f"{c[0]} - {c[1]}" for c in customers]
    
    def add_item_to_list(self):
        try:
            desc = self.desc_entry.get().strip()
            hsn = self.hsn_entry.get().strip()
            qty = int(self.qty_entry.get())
            rate = float(self.rate_entry.get())
            gst_rate = float(self.gst_entry.get())
            
            if not desc or qty <= 0 or rate <= 0:
                messagebox.showerror("Error", "Invalid item details")
                return
            
            amount = qty * rate
            self.current_items.append({
                'description': desc,
                'hsn': hsn,
                'qty': qty,
                'rate': rate,
                'gst_rate': gst_rate,
                'amount': amount
            })
            
            self.item_tree.insert('', 'end', values=(desc, hsn, qty, f"₹{rate:.2f}", f"{gst_rate}%", f"₹{amount:.2f}"))
            
            self.desc_entry.delete(0, tk.END)
            self.hsn_entry.delete(0, tk.END)
            self.qty_entry.delete(0, tk.END)
            self.rate_entry.delete(0, tk.END)
            self.gst_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for Qty, Rate, GST%")
    
    def clear_items(self):
        self.current_items.clear()
        for item in self.item_tree.get_children():
            self.item_tree.delete(item)
    
    def create_invoice(self):
        cust_selection = self.cust_combo.get()
        if not cust_selection or not self.current_items:
            messagebox.showerror("Error", "Select customer and add items")
            return
        
        try:
            customer_id = int(cust_selection.split('-')[0].strip())
        except:
            messagebox.showerror("Error", "Invalid customer selection")
            return
        
        invoice_no = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{len(db.get_invoices())+1:03d}"
        
        inv_id = db.add_invoice(invoice_no, customer_id, self.current_items)
        
        inv, items = db.get_invoice_details(inv_id)
        customers = db.get_customers()
        customer = next((c for c in customers if c[0] == customer_id), None)
        
        if customer:
            pdf_name = f"invoice_{invoice_no}.pdf"
            invoice.generate_pdf(inv, customer, items, pdf_name)
            messagebox.showinfo("Success", f"Invoice created! PDF: {pdf_name}")
            if os.path.exists(pdf_name):
                try:
                    os.startfile(pdf_name) if hasattr(os, 'startfile') else os.system(f'xdg-open "{pdf_name}"')
                except:
                    pass
            self.load_invoices()
            self.clear_items()
        else:
            messagebox.showerror("Error", "Failed to generate PDF")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()