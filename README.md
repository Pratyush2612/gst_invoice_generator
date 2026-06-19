# Invoice & GST Bill Generator

A simple Python application for shops, agencies, and distributors to generate GST-compliant invoices in PDF format. Includes customer management, invoice creation, payment tracking.

## Features
- Add and manage customers
- Create invoices with multiple items, GST calculation (CGST, SGST, IGST)
- Generate professional PDF invoices
- Track payment status
- View records and summaries
- SQLite database for persistence

## Requirements
- Python 3.8+
- reportlab (for PDF)
- pandas (optional, for reports)
- tkinter (for GUI, optional)

Install: `pip install reportlab pandas`

## Usage
Run `python main.py` for console interface.

Run `python gui.py` for full-featured Tkinter GUI.

## Project Structure
- main.py: Console app
- gui.py: Tkinter GUI application (recommended)
- db.py: Database operations
- invoice.py: Invoice and PDF generation
- invoices.db: SQLite database

## Additional Features Added
- Full Tkinter GUI with tabs
- Sample data (customers + 1 invoice)
- Excel export of invoices (using pandas)
- Improved buttons and status handling

## Sample Data
- Rahul Traders (Bangalore)
- Sharma Enterprises (Mumbai)
- Sample invoice INV-20260616-001

Run `python gui.py` to see everything populated.
