
# GST Invoice Generator (Python + MySQL)

A complete Python-based GST Invoice Generator that automates billing, GST calculation, product management, and generates professional Word invoices using DocxTemplate. The system uses MySQL for storing invoices, products, totals, and customer details.

------------------------------------------------------------
📌 FEATURES
------------------------------------------------------------
- Login & Signup (Admin/User roles)
- Create Invoice with customer + multiple products
- Automatic GST calculation:
  • SGST + CGST for Gujarat customers (state code 24)
  • IGST for all other states
- Store invoices in MySQL
- Update product row
- Delete product or entire invoice
- Search invoice by invoice number
- Read all invoices
- Auto-generate invoice DOCX using DocxTemplate
- Tkinter message alerts

------------------------------------------------------------
🛠 TECH STACK
------------------------------------------------------------
- Python
- MySQL
- DocxTemplate
- Tkinter MessageBox

------------------------------------------------------------
📁 PROJECT STRUCTURE
------------------------------------------------------------
GST-Invoice-Generator/
│── invoicefin.py
│── invoice_final.docx
│── requirements.txt
│── README.txt

------------------------------------------------------------
📦 REQUIREMENTS FILE (requirements.txt)
------------------------------------------------------------
mysql-connector-python
docxtpl
python-docx
tk

------------------------------------------------------------
⚙️ INSTALLATION
------------------------------------------------------------
1. Install Python 3.x  
2. Install MySQL Server  
3. Create a database named 'project'

Run:
    pip install -r requirements.txt

------------------------------------------------------------
🗄️ MYSQL DATABASE SETUP
------------------------------------------------------------
CREATE DATABASE project;

Tables needed:
- login
- info
- product
- final

(Structure already included inside Python code)

------------------------------------------------------------
▶️ HOW TO RUN THE PROJECT
------------------------------------------------------------
1. Make sure MySQL server is running
2. Place invoice_final.docx template in project folder
3. Run the script:

    python invoicefin.py

4. Choose Login or Signup
5. Use menu to create, update, delete, or search invoices.

------------------------------------------------------------
📄 OUTPUT
------------------------------------------------------------
• A detailed invoice is generated as a .docx file  
• Product-wise GST  
• Final amount calculation  
• Customer and invoice details printed

