import db
import invoice
import datetime
import os

def main():
    db.init_db()
    print("=== GST Invoice Generator ===")
    
    while True:
        print("\n1. Add Customer")
        print("2. Create Invoice")
        print("3. View Customers")
        print("4. View Invoices")
        print("5. Generate PDF for Invoice")
        print("6. Update Payment Status")
        print("7. Exit")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            name = input("Customer Name: ")
            gstin = input("GSTIN (optional): ")
            address = input("Address: ")
            phone = input("Phone: ")
            db.add_customer(name, gstin, address, phone)
            print("Customer added.")
        
        elif choice == '2':
            name = input("Customer Name: ")
            # Find customer
            customers = db.get_customers()
            customer = None
            for c in customers:
                if c[1].lower() == name.lower():
                    customer = c
                    break
            if not customer:
                print("Customer not found. Add first.")
                continue
            customer_id = customer[0]
            
            invoice_no = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{len(db.get_invoices())+1}"
            items = []
            while True:
                desc = input("Item description (or done): ")
                if desc.lower() == 'done':
                    break
                hsn = input("HSN: ")
                qty = int(input("Qty: "))
                rate = float(input("Rate: "))
                gst_rate = float(input("GST Rate %: "))
                items.append({'description': desc, 'hsn': hsn, 'qty': qty, 'rate': rate, 'gst_rate': gst_rate})
            
            inv_id = db.add_invoice(invoice_no, customer_id, items)
            print(f"Invoice created with ID: {inv_id}")
        
        elif choice == '3':
            customers = db.get_customers()
            for c in customers:
                print(c)
        
        elif choice == '4':
            invoices = db.get_invoices()
            for i in invoices:
                print(i)
        
        elif choice == '5':
            inv_id = int(input("Invoice ID: "))
            inv, items = db.get_invoice_details(inv_id)
            if not inv:
                print("Not found")
                continue
            customers = db.get_customers()
            customer = next((c for c in customers if c[0] == inv[3]), None)
            if customer:
                pdf_name = f"invoice_{inv[1]}.pdf"
                invoice.generate_pdf(inv, customer, items, pdf_name)
            else:
                print("Customer not found")
        
        elif choice == '6':
            inv_id = int(input("Invoice ID: "))
            status = input("Status (Paid/Pending): ")
            db.update_payment_status(inv_id, status)
            print("Updated.")
        
        elif choice == '7':
            break

if __name__ == "__main__":
    main()
