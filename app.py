import streamlit as st
import pandas as pd
import datetime
import os
import db
import invoice

st.set_page_config(page_title="GST Invoice Generator", layout="wide")
st.title("🧾 GST Invoice & Bill Generator")

# Company Logo Management
st.sidebar.header("Company Settings")
logo_file = st.sidebar.file_uploader("Upload Company Logo", type=['png', 'jpg', 'jpeg'])
logo_path = None

if logo_file:
    logo_path = f"logo_{logo_file.name}"
    with open(logo_path, "wb") as f:
        f.write(logo_file.getbuffer())
    st.sidebar.success("Logo uploaded successfully!")

# Initialize DB
db.init_db()

# Sidebar Navigation
page = st.sidebar.selectbox("Go to", ["Dashboard", "Customers", "Invoices", "Create New Invoice", "Reports"])

if page == "Dashboard":
    st.header("Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", len(db.get_customers()))
    with col2:
        invoices = db.get_invoices()
        st.metric("Total Invoices", len(invoices))
    with col3:
        pending = len([i for i in invoices if i[-1] == 'Pending'])
        st.metric("Pending Payments", pending, delta="⚠️")

elif page == "Customers":
    st.header("Customers")
    customers = db.get_customers()
    if customers:
        df = pd.DataFrame(customers, columns=['ID', 'Name', 'GSTIN', 'Address', 'Phone', 'Email'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No customers yet.")

    if st.button("➕ Add New Customer"):
        with st.form("add_customer"):
            name = st.text_input("Customer Name*")
            gstin = st.text_input("GSTIN")
            address = st.text_area("Address")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Save Customer")
            if submitted and name:
                db.add_customer(name, gstin, address, phone, email)
                st.success("Customer added successfully!")
                st.rerun()

elif page == "Invoices":
    st.header("All Invoices")
    invoices = db.get_invoices()
    if invoices:
        df = pd.DataFrame(invoices, columns=['ID', 'Invoice No', 'Date', 'Customer ID', 'Subtotal', 'CGST', 'SGST', 'IGST', 'Total', 'Status'])
        st.dataframe(df, use_container_width=True)
        
        selected_id = st.selectbox("Select Invoice to Generate PDF", [i[0] for i in invoices])
        if st.button("Generate PDF"):
            inv, items = db.get_invoice_details(selected_id)
            customers = db.get_customers()
            customer = next((c for c in customers if c[0] == inv[3]), None)
            if customer:
                pdf_name = f"invoice_{inv[1]}.pdf"
                invoice.generate_pdf(inv, customer, items, pdf_name, logo_path)
                st.success(f"PDF Generated: {pdf_name}")
                with open(pdf_name, "rb") as f:
                    st.download_button("Download PDF", f, file_name=pdf_name)
            else:
                st.error("Customer not found")
    else:
        st.info("No invoices yet.")

elif page == "Create New Invoice":
    st.header("Create New Invoice")
    
    customers = db.get_customers()
    customer_options = {f"{c[0]} - {c[1]}": c[0] for c in customers}
    selected_customer = st.selectbox("Select Customer", options=list(customer_options.keys()))
    customer_id = customer_options[selected_customer]
    
    st.subheader("Add Items")
    
    if 'items' not in st.session_state:
        st.session_state.items = []
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        desc = st.text_input("Description")
    with col2:
        hsn = st.text_input("HSN", value="")
    with col3:
        qty = st.number_input("Qty", min_value=1, value=1)
    with col4:
        rate = st.number_input("Rate (₹)", min_value=0.0, value=0.0, step=10.0)
    with col5:
        gst_rate = st.number_input("GST %", min_value=0.0, value=18.0, step=0.5)
    
    if st.button("Add Item"):
        if desc and rate > 0:
            amount = qty * rate
            st.session_state.items.append({
                'description': desc,
                'hsn': hsn,
                'qty': qty,
                'rate': rate,
                'gst_rate': gst_rate,
                'amount': amount
            })
            st.success("Item added!")
    
    if st.session_state.items:
        items_df = pd.DataFrame(st.session_state.items)
        st.dataframe(items_df, use_container_width=True)
        
        if st.button("Create Invoice & Generate PDF"):
            invoice_no = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{len(db.get_invoices())+1:03d}"
            inv_id = db.add_invoice(invoice_no, customer_id, st.session_state.items)
            
            inv, items = db.get_invoice_details(inv_id)
            customers_list = db.get_customers()
            customer = next((c for c in customers_list if c[0] == customer_id), None)
            
            if customer:
                pdf_name = f"invoice_{invoice_no}.pdf"
                invoice.generate_pdf(inv, customer, items, pdf_name, logo_path)
                st.success(f"Invoice Created Successfully! Invoice No: {invoice_no}")
                
                with open(pdf_name, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_name, mime="application/pdf")
                
                st.session_state.items = []
                st.rerun()
    else:
        st.warning("Add at least one item")

elif page == "Reports":
    st.header("Reports")
    if st.button("Export All Invoices to Excel"):
        try:
            invoices = db.get_invoices()
            df = pd.DataFrame(invoices, columns=['ID', 'Invoice No', 'Date', 'Customer ID', 'Subtotal', 'CGST', 'SGST', 'IGST', 'Total', 'Status'])
            filename = f"invoices_report_{datetime.date.today()}.xlsx"
            df.to_excel(filename, index=False)
            st.success(f"Report saved as {filename}")
            with open(filename, "rb") as f:
                st.download_button("Download Excel Report", f, file_name=filename)
        except Exception as e:
            st.error(f"Error: {e}")

st.sidebar.info("Company Logo is automatically used in generated PDFs.")