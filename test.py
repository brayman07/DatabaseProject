import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from _datetime import datetime

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="33y&()5I",
        database="databaseproj"
    )


def open_crud_window(table_name):
    crud_window = tk.Toplevel()
    crud_window.title(f"CRUD Operations for {table_name}")

    cols = {
        "ProductInformation": ('ProductID', 'ProductName', 'Description', 'QuantityOnHand', 'ReorderPoint'),
        "SupplierInformation": ('SupplierID', 'SupplierName', 'Address', 'ContactInfo'),
        "PurchaseOrderInformation": ('PurchaseOrderID', 'Date', 'SupplierID', 'ItemsOrdered'),
        "ReceivingInformation": ('ReceivingNumber', 'Date', 'SupplierID', 'ItemsReceived'),
        "SalesOrderInformation": ('SalesOrderID', 'Date', 'Customer', 'ItemsOrdered'),
        "ShippingInformation": ('ShippingNumber', 'Date', 'Customer', 'ItemsShipped')
    }[table_name]

    tree = ttk.Treeview(crud_window, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    def load_data():
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert('', 'end', values=row)
        db.close()

    def display_join_query():
        if table_name == "PurchaseOrderInformation":
            join_window = tk.Toplevel()
            join_window.title("Purchase Orders and Supplier Details")

            join_tree = ttk.Treeview(join_window, columns=("PurchaseOrderID", "Date", "SupplierName", "ItemsOrdered"),
                                     show='headings')
            for col in ("PurchaseOrderID", "Date", "SupplierName", "ItemsOrdered"):
                join_tree.heading(col, text=col)
            join_tree.pack(expand=True, fill='both')

            query = """
            SELECT p.PurchaseOrderID, p.Date, s.SupplierName, p.ItemsOrdered
            FROM PurchaseOrderInformation p
            JOIN SupplierInformation s ON p.SupplierID = s.SupplierID
            """
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                join_tree.insert('', 'end', values=row)
            db.close()

    # Place button to trigger the join query, only visible for the PurchaseOrderInformation table
    if table_name == "PurchaseOrderInformation":
        tk.Button(crud_window, text="Show Purchase Orders with Suppliers", command=display_join_query).pack(
            side=tk.LEFT, padx=10, pady=10)

    def add_entry():
        add_window = tk.Toplevel(crud_window)
        add_window.title("Add New Entry")
        entries = {col: tk.Entry(add_window) for col in cols}
        for col in cols:
            tk.Label(add_window, text=col).pack()
            entry = entries[col]
            if 'Date' in col:  # Special handling for date fields
                entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            entry.pack()

        def submit():
            values = [entry.get() for entry in entries.values()]
            db = get_db_connection()
            cursor = db.cursor()
            try:
                cursor.execute(f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(values))})", values)
                db.commit()
                messagebox.showinfo("Success", "Entry added successfully")
            except mysql.connector.Error as err:
                db.rollback()
                messagebox.showerror("Error", "Failed to add entry: " + str(err))
            finally:
                db.close()
                add_window.destroy()
                load_data()

        tk.Button(add_window, text="Submit", command=submit).pack()

    def delete_entry():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No item selected")
            return
        selected_item = selected_item[0]
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE {cols[0]} = %s", (tree.set(selected_item, '#1'),))
            db.commit()
            tree.delete(selected_item)
            messagebox.showinfo("Success", "Entry deleted successfully")
        except mysql.connector.Error as err:
            db.rollback()
            messagebox.showerror("Error", "Failed to delete entry: " + str(err))
        finally:
            db.close()

    def update_entry():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No item selected")
            return
        selected_item = selected_item[0]
        current_values = tree.item(selected_item, 'values')
        update_window = tk.Toplevel(crud_window)
        update_window.title("Update Entry")
        entries = {col: tk.Entry(update_window) for col in cols}
        for col, value in zip(cols, current_values):
            tk.Label(update_window, text=col).pack()
            entry = entries[col]
            entry.insert(0, value)
            entry.pack()

        def submit_update():
            new_values = [entry.get() for entry in entries.values()]
            db = get_db_connection()
            cursor = db.cursor()
            update_columns = ', '.join([f"{col} = %s" for col in cols])
            update_query = f"UPDATE {table_name} SET {update_columns} WHERE {cols[0]} = %s"
            cursor.execute(update_query, new_values + [current_values[0]])  # Add PK at the end
            db.commit()
            db.close()
            update_window.destroy()
            load_data()

        tk.Button(update_window, text="Submit Changes", command=submit_update).pack()

    # Place buttons for CRUD operations
    tk.Button(crud_window, text="Load Data", command=load_data).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(crud_window, text="Add Entry", command=add_entry).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(crud_window, text="Delete Selected Entry", command=delete_entry).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(crud_window, text="Update Selected Entry", command=update_entry).pack(side=tk.LEFT, padx=10, pady=10)

    load_data()

def open_main_window():
    main_window = tk.Tk()
    main_window.title("Database Management System")

    tables = ["ProductInformation", "SupplierInformation", "PurchaseOrderInformation",
              "ReceivingInformation", "SalesOrderInformation", "ShippingInformation"]

    for table in tables:
        tk.Button(main_window, text=f"Manage {table}", command=lambda t=table: open_crud_window(t)).pack()

    main_window.mainloop()

def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "admin":
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password")

login_window = tk.Tk()
login_window.title("Login")

tk.Label(login_window, text="Username:").pack()
username_entry = tk.Entry(login_window)
username_entry.pack()

tk.Label(login_window, text="Password:").pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

tk.Button(login_window, text="Login", command=login).pack()

login_window.mainloop()