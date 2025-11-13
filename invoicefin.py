import tkinter as tk
from tkinter import messagebox
import mysql.connector as m
from docxtpl import DocxTemplate
import datetime
final=0 
total=0
total_sgst, total_cgst, total_igst = 0, 0, 0

def establish_connection():
    return m.connect(host="localhost", user="root", password="Sujal", database="project")


def signup():
    try:
        srno = int(input("Enter Srno No: "))
        username = input("Enter Username: ")
        password = input("Enter your Password: ")
        role = input("Enter your Role (admin/user): ")

        con = establish_connection()
        wire = con.cursor()
        wire.execute("INSERT INTO login (Srno, username, password, role) VALUES({}, '{}', '{}', '{}')".format(srno, username, password, role))
        con.commit()
        messagebox.showinfo("Success", "Data Successfully Added")
        con.close()
        wire.close()
        login()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def login():
    try:
        print("\n Enter Your Login Credentials \n")
        username = input("Enter Username: ")
        password = input("Enter your Password: ")

        con = establish_connection()
        wire = con.cursor()
        wire.execute("SELECT role FROM login WHERE username = %s AND password = %s", (username, password))
        role = wire.fetchone()

        if role:
            if role[0] == 'admin':
                mainpage_admin()
            elif role[0] == 'user':
                mainpage_user()
            else:
                print("Invalid role.")
        else:
            messagebox.showwarning("Invalid", "Invalid username or password")

        con.close()
        wire.close()
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

def create():
    try:
        # Establish a database connection
        con = establish_connection()
        wire = con.cursor()

        # Get customer details
        invoice = int(input("Enter invoice No: "))
        custna = input("Enter the Customer Name: ")
        contno = int(input("Enter Customer's Mobile Number: "))
        gst_no = input("Enter the GST number (e.g., 24XXXXXXXX): ")

        sgst, cgst, igst = 0, 0, 0

        if gst_no[:2] == "24":
            sgst = 0.09  # 9% SGST
            cgst = 0.09  # 9% CGST
        else:
            igst = 0.18  # 18% IGST

        # Insert customer details into the database
        wire.execute("INSERT INTO info (Inno, Cus_name, mobno, Gstno) VALUES (%s, %s, %s, %s)",
                     (invoice, custna, contno, gst_no))
        con.commit()

        # Create a list to store invoice data
        invoice_list = []

        x = int(input("Enter How Many Products you Require: "))

        for i in range(x):
            sr = int(input("Enter Your Sr No: "))
            des = input("Enter description: ")
            qty = int(input("Enter Quantity: "))
            pr = float(input("Enter Price: "))

            ta = pr * qty
            sgst_a = ta * sgst
            cgst_a = ta * cgst
            igst_a = ta * igst
            tot_gst = ta + sgst_a + cgst_a + igst_a
            global total
            total += tot_gst
            global final
            final = total
           
           #for total Gst in docx document..
            global total_sgst, total_cgst, total_igst
            total_sgst += sgst_a
            total_cgst += cgst_a
            total_igst += igst_a
            
            item_data = (sr, des, qty, pr, ta)
            invoice_list.append(item_data)

            # Insert product details into the database
            wire.execute("INSERT INTO product (sr, Description, Qty, price, Net_tot, sgst, cgst, igst, Total, Inno) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                         (sr, des, qty, pr, ta, sgst_a, cgst_a, igst_a, tot_gst, invoice))
            con.commit()


        # Insert the final total into the database
        wire.execute("INSERT INTO final (final, Inno) VALUES (%s, %s)", (final, invoice))
        con.commit()

        con.close()

        # Generate the invoice document
        generate_document(invoice, custna, contno, gst_no, invoice_list, total_cgst, total_sgst, total_igst, final)
        messagebox.showinfo("Success", "Data Successfully Stored")

    except m.Error as err:
        messagebox.showerror("MySQL Error", f"An error occurred: {err}")
        
        
def generate_document(invoice, name, number, gst, invoice_items,cgst,sgst,igst,final):
    try:
        # Generate the invoice as a Word document
        doc = DocxTemplate("invoice_final.docx")
        date = datetime.datetime.now()
        doc.render({"invoice": invoice, "name": name, "phone": number, "gst": gst, "date": date,
                    "invoice_list": invoice_items, "cgst":cgst, "sgst":sgst, "igst":igst,"final":final})

        # Define the output file name
        doc_name = "invoice_{}_{}.docx".format(name, date.strftime("%Y-%m-%d-%H%M%S"))

        # Save the generated invoice
        doc.save(doc_name)
        messagebox.showinfo("Invoice Complete", "Invoice saved as {}".format(doc_name))

    except Exception as e:
        messagebox.showerror("Error", str(e))


def read_all_invoices():
    try:
        con = m.connect(host="localhost", user="root", password="Sujal", database="project")
        wire = con.cursor()

        wire.execute("SELECT info.Inno, Cus_name, mobno, Gstno, final.final FROM info JOIN final ON info.Inno = final.Inno")
        invoices_data = wire.fetchall()

        con.close()

        if invoices_data:
            print("\nList of All Invoices:")
            print("Inno\tName\t\tMobile No\t\tGST NO\t\tTotal")

            for invoice in invoices_data:
                invoice_number, customer_name, contact_number, gst_number, total = invoice
                print(f"{invoice_number}\t{customer_name}\t{contact_number}\t{gst_number}\t{total}")

        else:
            print("No invoices found in the database.")

    except m.Error as err:
        print(f"An error occurred: {err}")
        
        
def display_invoice(invoice_data):
    try:
        invoice_number, customer_name, contact_number, gst_number, *extra_values = invoice_data


        con = establish_connection()
        wire = con.cursor()

        # Execute a query to fetch product data related to the invoice
        wire.execute("SELECT sr, Description, Qty, price, Net_tot, sgst, cgst, igst, Total FROM Product WHERE Inno = %s", (invoice_number,))
        product_data = wire.fetchall()

        # Execute a query to fetch total data related to the invoice
        wire.execute("SELECT final FROM final WHERE Inno = %s", (invoice_number,))
        total_data = wire.fetchone()

        wire.close()
        con.close()

        # Process and display the retrieved data
        print("\nInvoice Details:\n")
        
        print(f"Invoice Number: {invoice_number}")
        print(f"Customer Name: {customer_name}")
        print(f"Contact Number: {contact_number}")
        print(f"GST Number: {gst_number}\n")

        # Display product data
        max_qty_length = max(len(str(item[1])) for item in product_data)
        header = f"Sr\tDescription{' ' * (max_qty_length - 4)}Qty\tPrice\tNet\tSGST\tCGST\tIGST\tTotal"

        total_header_length = len(header)
        add_dots = 30

        total_dotted_line_length = total_header_length + add_dots
        dotted_line = '_' * total_dotted_line_length

        # Print the column headers and the dotted line
        print(header)
        print(dotted_line)
        for product in product_data:
            sr, description, qty, price, net_total, sgst, cgst, igst, total = product
            print(f"{sr}\t{description}\t{qty}\t{price}\t{net_total}\t{sgst}\t{cgst}\t{igst}\t{total}")

        # Display the total value
        print(dotted_line)
    
        print(f"\nTotal (with 18% GST): {total_data[0]}\n")

    except Exception as e:
        print(f"An error occurred: {e}")


def search_invoice():
    try:
        invoice_to_search = int(input("Enter Invoice Number to Search: "))

        con = establish_connection()
        wire = con.cursor()

        # Execute a query to fetch the invoice data based on the provided invoice number
        wire.execute("SELECT * FROM info WHERE Inno = %s", (invoice_to_search,))
        invoice_data = wire.fetchone()

        if invoice_data:
            print(f"Found invoice {invoice_to_search}.")
            display_invoice(invoice_data)
            user_input = input("Do you want to continue (C) ").lower()
            if user_input != 'c':
                print("Thank You")

        else:
            print(f"No Such Invoice {invoice_to_search} Found")

        wire.close()
        con.close()
    except Exception as e:
        print(f"An error occurred: {e}")

        


def delete_row():
    try:
        srno = int(input("Enter Srno you want to delete : "))


        con = establish_connection()
        wire = con.cursor()
        to_del= srno
        del_query = "Delete From product where sr = %s"
        wire.execute(del_query,(to_del,))
        con.commit()
        messagebox.showinfo("Success", "Data Successfully Added")
        con.close()
        wire.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))
        

def delete():
    try:
        inv_no = int(input("Enter the Invoice no to delete :"))

        con = establish_connection()
        wire = con.cursor()
        to_del = (inv_no,)
        del_query1="Delete from info where Inno=%s"
        del_query2="Delete from product where Inno=%s"
        del_query3="Delete from final where Inno=%s"

        wire.execute(del_query1, to_del)
        wire.execute(del_query2, to_del)
        wire.execute(del_query3, to_del)

        con.commit()
        messagebox.showinfo("Success", "Data Successfully deleted")
        con.close()
        wire.close()

    except Exception as e:
        messagebox.showerror("Error",str(e))
    
def update_row():
    try:
        # Establish a database connection
        con = establish_connection()
        wire = con.cursor()
        # Get Invoice No. and Sr. No. to update
        invoice_number = int(input("Enter Invoice Number: "))
        sr_to_update = int(input("Enter Sr. No. to update: "))

        # Check if the Sr. No. exists in the database for the given Invoice No.
        wire.execute("SELECT * FROM product WHERE Inno = %s AND sr = %s", (invoice_number, sr_to_update))
        row_exists = wire.fetchone()
        
        wire.execute("Select Gstno from info where Inno =%s",(invoice_number,))
        gst_exists= wire.fetchone()

        if row_exists:
            # Get new data similar to the create function
            new_sr = int(input("Enter new Sr No: "))
            new_description = input("Enter new description: ")
            new_qty = int(input("Enter new Quantity: "))
            new_price = float(input("Enter new Price: "))

            sgst, cgst, igst = 0, 0, 0

            if gst_exists and gst_exists[0][:2] == "24":
                sgst = 0.09  # 9% SGST
                cgst = 0.09  # 9% CGST
            else:
                igst = 0.18  # 18% IGST

            # Calculate new totals based on new data
            new_ta = new_price * new_qty
            new_sgst = new_ta * sgst
            new_cgst = new_ta * cgst
            new_igst = new_ta * igst
            new_tot_gst = new_ta + new_sgst + new_cgst + new_igst

            # Update the row with new data and calculated GST
            update_query = "UPDATE product SET sr = %s, Description = %s, Qty = %s, price = %s, Net_tot = %s, sgst = %s, cgst = %s, igst = %s, Total = %s WHERE Inno = %s AND sr = %s"
            wire.execute(update_query, (new_sr, new_description, new_qty, new_price, new_ta, new_sgst, new_cgst, new_igst, new_tot_gst, invoice_number, sr_to_update))
            
            update_query1 = "UPDATE final SET final = (SELECT SUM(Total) FROM product WHERE Inno = %s) WHERE Inno = %s"
            wire.execute(update_query1,(invoice_number,invoice_number))
            con.commit()
            
            messagebox.showinfo("Success", f"Row with Sr. No. {sr_to_update} updated successfully for Invoice No. {invoice_number}")
        else:
            messagebox.showwarning("Not Found", f"No row with Sr. No. {sr_to_update} found for Invoice No. {invoice_number}")

    except m.Error as err:
        messagebox.showerror("MySQL Error", f"An error occurred: {err}")
    except ValueError:
        messagebox.showerror("Input Error", "Invalid input. Please enter valid numbers.")
    except PermissionError:
        messagebox.showerror("Permission Denied", "Cannot access or write to the file. Please check file permissions.")
    finally:
        # Close the database connection
        con.close()



                
def exit():
    while True:
        user_input = input("Do you want to exit the application? (yes/no): ").strip().lower()
        if user_input == 'yes':
            print("Exiting the application. Thank you for using our system.")
            break 
        elif user_input == 'no':
            print("Returning to the main menu.")
            break  
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def mainpage_admin():
    ans = 'y'
    while ans=='y':
        messagebox.showinfo("Welcome", "Welcome to Bhandari's Electronic Store")
        messagebox.showinfo("Main Menu", "*** Main Menu ***\n"
                                        "1. To Create an Invoice Bill\n"
                                        "2. To Read the Invoice Detail\n"
                                        "3. To Search the Invoice Detail\n"
                                        "4. To Delete the Product Detail\n"
                                        "5. To Update the Product Detail\n"
                                        "6. Exit ")

        ch1 = int(input("Enter Your Choice: "))
        if ch1 == 1:
            create()
        if ch1 == 2:
            read_all_invoices()
        if ch1 == 3:
            search_invoice()
        if ch1 == 4:
            delete()
        if ch1 == 5:
            update_row()
        if ch1 == 6:
            exit()
            break


def mainpage_user():
    while True:
        print("\nUser Menu:")
        print("1. Create Invoice")
        print("2. Update Invoice")
        print("3. Exit")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            create()
        elif choice == 2:
            update_row ()
        elif choice == 3:
            break
        else:
            print("Invalid choice. Please try again.")

    # You can continue the loop for other user-specific actions


# Add these lines at the end of the script to start the GUI loop
root = tk.Tk()
root.withdraw()  # Hide the root window

print("\n\n Welcome To Mukesh  Engineering Works")
print("*** Login OR Signup ***")
print("1.To Create Signup ")
print("2.To Login ")

ch=int(input("Enter Your Choice="))
if ch==1:
        signup()
if ch==2:
        login()


root.mainloop()  # Start the GUI loop
