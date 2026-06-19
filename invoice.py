from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import datetime

def generate_pdf(invoice, customer, items, filename='invoice.pdf'):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 1*inch, "GST INVOICE")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.5*inch, "Shop Name: Your Business Name")
    c.drawString(1*inch, height - 1.7*inch, "Address: Your Address, City")
    c.drawString(1*inch, height - 1.9*inch, "GSTIN: YOURGSTIN12345")
    c.drawString(1*inch, height - 2.1*inch, f"Invoice No: {invoice[1]}")
    c.drawString(1*inch, height - 2.3*inch, f"Date: {invoice[2]}")
    
    # Customer Info
    c.drawString(1*inch, height - 3*inch, "Bill To:")
    c.drawString(1*inch, height - 3.2*inch, customer[1])  # name
    if customer[2]:  # gstin
        c.drawString(1*inch, height - 3.4*inch, f"GSTIN: {customer[2]}")
    c.drawString(1*inch, height - 3.6*inch, customer[3])  # address
    
    # Table for items
    data = [['Description', 'HSN', 'Qty', 'Rate', 'Amount', 'GST%']]
    for item in items:
        data.append([item[2], item[3], str(item[4]), f"₹{item[5]:.2f}", f"₹{item[6]:.2f}", f"{item[7]}%"])
    
    table = Table(data, colWidths=[3*cm, 2*cm, 1.5*cm, 2*cm, 2*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 1*inch, height - 6*inch)
    
    # Totals
    y = height - 7.5*inch
    c.drawString(4*inch, y, f"Subtotal: ₹{invoice[4]:.2f}")
    c.drawString(4*inch, y - 0.3*inch, f"CGST: ₹{invoice[5]:.2f}")
    c.drawString(4*inch, y - 0.6*inch, f"SGST: ₹{invoice[6]:.2f}")
    c.drawString(4*inch, y - 0.9*inch, f"IGST: ₹{invoice[7]:.2f}")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(4*inch, y - 1.3*inch, f"Total: ₹{invoice[8]:.2f}")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, 1*inch, "Thank you for your business! Payment due within 15 days.")
    c.drawString(1*inch, 0.7*inch, "This is a computer generated invoice.")
    
    c.save()
    print(f"PDF generated: {filename}")
