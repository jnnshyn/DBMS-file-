from PyQt5 import QtCore, QtGui, QtWidgets
from SC import Ui_Sugarcafe
from Login import Ui_MainWindow
from Dashboard import Ui_dashboard
import psycopg2
from PyQt5.QtWidgets import QInputDialog, QTableWidgetItem
import sys
import re
from datetime import datetime 
import decimal
import re
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox, QMessageBox, QTableWidgetItem
from PyQt5.QtWidgets import QLabel, QSpinBox, QComboBox, QCalendarWidget, QVBoxLayout, QDialog, QDialogButtonBox, QMessageBox
from pymongo import MongoClient
from PyQt5.QtCore import Qt

# Log in window
class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # Assuming this UI class is already defined
        self.ui.setupUi(self)
        self.ui.login.clicked.connect(self.check_login)  # Connecting login button to check_login method
        self.show()
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["SugarCafe"]
        

    def check_login(self):
        username = self.ui.username.text()
        password = self.ui.password.text()

        if username == "admin" and password == "admin123":
            # Show success message modal
            QtWidgets.QMessageBox.information(self, "Success", "Successfully logged in!")

            # Open the dashboard window and close the login window
            self.dashboard_window = Dashboard()  # Create an instance of the dashboard window
            self.dashboard_window.show()  # Show the dashboard window
            self.close()  # Close the login window

        else:
            # Show error message if login fails
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid username or password")
            
            # Clear username and password fields
            self.ui.username.clear()
            self.ui.password.clear()

            # Focus back to the username input field
            self.ui.username.setFocus()
           


# Main Dashboard class
class Dashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_dashboard()  # Assuming this UI class is already defined
        self.ui.setupUi(self)

        # Connect buttons to their respective methods
        self.ui.Inventory_DB.clicked.connect(self.show_sugar_cafe_inventory)
        self.ui.Order_DB.clicked.connect(self.show_sugar_cafe_order)
        self.ui.Report_DB.clicked.connect(self.show_sugar_cafe_report)
        self.ui.Supplier_DB.clicked.connect(self.show_sugar_cafe_supplier)
        # Connect the logout button to the logout confirmation method
        self.ui.Logout_DB.clicked.connect(self.confirm_logout)

    def connect_to_database(self):
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client["SugarCafe"]

        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def show_sugar_cafe_inventory(self):
        self.connect_to_database()
        self.sugarcafe_window = Sugarcafe()
        self.sugarcafe_window.ui.stackedWidget.setCurrentWidget(self.sugarcafe_window.ui.InventoryPage)
        self.sugarcafe_window.refresh_product_table()  # Fetch data for InventoryPage
        self.sugarcafe_window.show()
        self.close()# Close the Dashboard window
        
    def show_sugar_cafe_order(self):
        try:
            self.connect_to_database()
            self.sugarcafe_window = Sugarcafe()
            self.sugarcafe_window.ui.stackedWidget.setCurrentWidget(self.sugarcafe_window.ui.OrderPage)
            self.sugarcafe_window.refresh_order_table()
            self.sugarcafe_window.show()
            self.close()

        except Exception as e:
            print(f"Error displaying order page: {e}")
        

    def show_sugar_cafe_report(self):
        try:
            self.connect_to_database()
            self.sugarcafe_window = Sugarcafe()
            self.sugarcafe_window.ui.stackedWidget.setCurrentWidget(self.sugarcafe_window.ui.SalesReportPage)  # Show SalesReportPage
            self.sugarcafe_window.CSR_page()  # Populate the SalesReportPage
            self.sugarcafe_window.show()  # Show the SugarCafe window
            self.close()  # Close the Dashboard window
        except Exception as e:
            print(f"Error displaying report page: {e}")

    def show_sugar_cafe_supplier(self):
        try:
            
            self.connect_to_database()
            self.sugarcafe_window = Sugarcafe(self.connection, self.cursor)
            self.sugarcafe_window.refresh_supplier_table()
            self.sugarcafe_window.ui.stackedWidget.setCurrentWidget(self.sugarcafe_window.ui.SupplierManagementPage)
            self.sugarcafe_window.show()
            self.close()
        except Exception as e:
            print(f"Error in show_sugar_cafe_supplier: {e}")

    
    # Method to confirm logout
    def confirm_logout(self):
        reply = QMessageBox.question(self, 'Confirm Logout', 
                                     'Are you sure you want to logout?', 
                                     QMessageBox.Yes | QMessageBox.No, 
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()  # Close the Dashboard window
            self.mainWindow = MainWindow()  # Reopen the login window
            self.mainWindow.show()  # Show the login window again


# SugarCafe Window
class Sugarcafe(QtWidgets.QMainWindow):
    def __init__(self, connection=None, cursor=None):
        super().__init__()
        self.ui = Ui_Sugarcafe()
        self.ui.setupUi(self)
        self.connection = connection  # Save connection
        self.cursor = cursor  # Save cursor
        self.connect_buttons()

      

        # Connect dashboard buttons to their respective pages
        self.ui.Dashboard_button.clicked.connect(self.dashboard)
        self.ui.Inventory.clicked.connect(self.inventory_page)
        self.ui.Order.clicked.connect(self.order_page)
        self.ui.Report.clicked.connect(self.CSR_page)
        self.ui.Supplier.clicked.connect(self.supplier_page)

        # Logout functionality
        self.ui.Logout.clicked.connect(self.logout)

    def dashboard(self):
        self.dashboard_window = Dashboard()  # Create an instance of the dashboard window
        self.dashboard_window.show()  # Show the dashboard window
        self.close()       

    def connect_buttons(self):
        #Inventory
        self.Editbutton = self.findChild(QtWidgets.QPushButton, 'Edit')
        self.Editbutton.clicked.connect(self.toggle_edit_mode)
        self.Addproductbutton = self.findChild(QtWidgets.QPushButton, 'Add')
        self.Addproductbutton.clicked.connect(self.add_product)
        self.Deletebutton = self.findChild(QtWidgets.QPushButton, 'Delete')
        self.Deletebutton.clicked.connect(self.delete_product)

        #Order
        self.Addordbutton = self.findChild(QtWidgets.QPushButton, 'Add_4')
        self.Addordbutton.clicked.connect(self.add_order)
        self.Editordbutton = self.findChild(QtWidgets.QPushButton, 'Edit_2')
        self.Editordbutton.clicked.connect(self.toggle_edit_mode_order)
        self.Deleteordbutton = self.findChild(QtWidgets.QPushButton, 'Delete_2')
        self.Deleteordbutton.clicked.connect(self.delete_order)

        #Supplier
        self.Addbutton = self.findChild(QtWidgets.QPushButton, 'Add_7')
        self.Addbutton.clicked.connect(self.add_supplier)
        self.Editsuppbutton = self.findChild(QtWidgets.QPushButton, 'Edit_5')
        self.Editsuppbutton.clicked.connect(self.toggle_edit_mode_supplier)
        self.Deletesuppbutton = self.findChild(QtWidgets.QPushButton, 'Delete_5')
        self.Deletesuppbutton.clicked.connect(self.delete_supplier)



    def connect_to_database(self): #database connection
        try:
            self.connection = psycopg2.connect(
                dbname="SugarCafe",
                user="postgres",
                password="09325365063",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            print("Database Connected")
        except Exception as e:
            print(f"Error connecting to database: {e}")


    #dashboard pages
    def inventory_page(self):
        self.connect_to_database()
        self.ui.stackedWidget.setCurrentWidget(self.ui.InventoryPage)
        self.ui.Inventory.setStyleSheet("QPushButton{background-color:rgb(223,203,171); border:null; border-radius:null; }")
        self.ui.Order.setStyleSheet(
            "QPushButton{ background-color: transparent; border:null} QPushButton:hover{background-color: rgba(244,237,228,200); border-radius: 20px;}")
        self.ui.Report.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.ui.Supplier.setStyleSheet(
            "QPushButton{background-color: transparent;; border:null} QPushButton:hover{background-color: rgba(244,237,228,200); border-radius: 20px;}")
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'InventoryTable')
       
        self.refresh_product_table()

    def add_product(self):
        self.connect_to_database()

        product_dialog = QDialog(self)
        product_dialog.setWindowTitle("Add Product")
        product_dialog.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: #333333;
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Form layout
        layout = QVBoxLayout(product_dialog)
        form_layout = QFormLayout()

        product_name_input = QLineEdit()
        product_qoh_input = QLineEdit()
        product_price_input = QLineEdit()
        product_desc_input = QTextEdit()
        supplier_id_input = QLineEdit()

        form_layout.addRow(QLabel("Product Name:"), product_name_input)
        form_layout.addRow(QLabel("Quantity on Hand:"), product_qoh_input)
        form_layout.addRow(QLabel("Product Price:"), product_price_input)
        form_layout.addRow(QLabel("Product Description:"), product_desc_input)
        form_layout.addRow(QLabel("Supplier ID:"), supplier_id_input)

        layout.addLayout(form_layout)

        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def on_accept():
            try:
                product_name = product_name_input.text()
                product_qoh = int(product_qoh_input.text())
                product_price = float(product_price_input.text())
                product_desc = product_desc_input.toPlainText()
                supp_id = int(supplier_id_input.text())

                if not product_name or not product_desc:
                    QMessageBox.warning(product_dialog, "Error", "Product Name and Description are required.")
                    return

                # Check supplier existence in MongoDB
                supplier_exists = self.db['SUPPLIER'].find_one({"SUPP_ID": supp_id})
                if not supplier_exists:
                    QMessageBox.warning(product_dialog, "Error", "Supplier ID does not exist.")
                    return

                # Generate Product ID
                last_productid = self.productdb.find_one(sort=[("_id", -1)])
                prod_id = (last_productid["_id"] + 1) if last_productid else 1

                # Insert product
                product = {
                    "_id": prod_id,
                    "product_name": product_name,
                    "quantity_on_hand": product_qoh,
                    "price": product_price,
                    "description": product_desc,
                    "supplier_id": supp_id
                }
                self.productdb.insert_one(product)

                # Refresh table
                row_position = self.ui.InventoryTable.rowCount()
                self.ui.InventoryTable.insertRow(row_position)
                self.ui.InventoryTable.setItem(row_position, 0, QTableWidgetItem(str(prod_id)))
                self.ui.InventoryTable.setItem(row_position, 1, QTableWidgetItem(product_name))
                self.ui.InventoryTable.setItem(row_position, 2, QTableWidgetItem(str(product_qoh)))
                self.ui.InventoryTable.setItem(row_position, 3, QTableWidgetItem(str(product_price)))
                self.ui.InventoryTable.setItem(row_position, 4, QTableWidgetItem(product_desc))
                self.ui.InventoryTable.setItem(row_position, 5, QTableWidgetItem(str(supp_id)))

                product_dialog.accept()

            except Exception as e:
                QMessageBox.warning(product_dialog, "Error", f"Failed to add product: {e}")

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(product_dialog.reject)
        product_dialog.exec_()

    def refresh_product_table(self):
        try:
            self.ui.Inventory.setStyleSheet("QPushButton{background-color:rgb(223,203,171); border:null; border-radius:null; }")
            self.ui.Order.setStyleSheet(
                "QPushButton{ background-color: transparent; border:null} QPushButton:hover{background-color: rgba(244,237,228,200); border-radius: 20px;}")
            self.ui.Report.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
            self.ui.Supplier.setStyleSheet(
                "QPushButton{background-color: transparent;; border:null} QPushButton:hover{background-color: rgba(244,237,228,200); border-radius: 20px;}")
    
        # Ensure connection is valid
            if not self.connection:
             raise Exception("Database connection is not established.")

        # Execute the query
            cursor = self.connection.cursor()
            cursor.execute("SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_QOH, PRODUCT_PRICE, PRODUCT_DESC, SUPP_ID FROM PRODUCT")
            products = cursor.fetchall()

        # Clear the table and set columns
            self.ui.InventoryTable.setRowCount(0)
            self.ui.InventoryTable.setColumnCount(6)  # Match the number of fields in the query
            self.ui.InventoryTable.setHorizontalHeaderLabels(
             ["Product ID", "Product Name", "Quantity on Hand", "Price", "Description", "Supplier ID"]
            )   

        # Populate the table with data
            for row_number, row_data in enumerate(products):
                self.ui.InventoryTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make uneditable
                    self.ui.InventoryTable.setItem(row_number, column_number, item)
        except Exception as e:
            print(f"Error fetching products: {e}")


    def toggle_edit_mode(self):
        if self.Editbutton.text() == "Save":
            if self.save_edited_data():  # Save changes and check if successful
                self.Editbutton.setText("Edit")
                for row in range(self.ui.InventoryTable.rowCount()):
                    for col in range(self.ui.InventoryTable.columnCount()):
                        item = self.ui.InventoryTable.item(row, col)
                        if item:
                            # Disable editing for all columns
                            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        else:  # If the text is "Edit"
            self.Editbutton.setText("Save")
            for row in range(self.ui.InventoryTable.rowCount()):
                for col in range(self.ui.InventoryTable.columnCount()):
                    item = self.ui.InventoryTable.item(row, col)
                    if item:
                        # Enable editing for all columns except the first and last
                        if col != 0 and col != 5:
                            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

    def save_edited_data(self):
        self.connect_to_database()
        try:
            edited = False  # Flag to track if any changes were saved
            for row in range(self.ui.InventoryTable.rowCount()):
                product_id = self.ui.InventoryTable.item(row, 0).text()
                product_name = self.ui.InventoryTable.item(row, 1).text()
                product_qoh = self.ui.InventoryTable.item(row, 2).text()
                product_price = self.ui.InventoryTable.item(row, 3).text()
                product_desc = self.ui.InventoryTable.item(row, 4).text()
                supp_id = self.ui.InventoryTable.item(row, 5).text()

                # Validate that the product_qoh is not negative
                if int(product_qoh) < 0:
                    QtWidgets.QMessageBox.warning(self, "Error", "Product Quantity On Hand cannot be negative")
                    return False

                # Validate that the product_price is not negative
                if float(product_price) < 0:
                    QtWidgets.QMessageBox.warning(self, "Error", "Product Price cannot be negative")
                    return False

                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE PRODUCT
                    SET PRODUCT_NAME = %s, PRODUCT_QOH = %s, PRODUCT_PRICE = %s, 
                        PRODUCT_DESC = %s, SUPP_ID = %s
                    WHERE PRODUCT_ID = %s
                """, (product_name, product_qoh, product_price, product_desc, supp_id, product_id))
                self.connection.commit()

                # Check if any changes were actually made and saved
                if cursor.rowcount > 0:
                    edited = True

            # If any changes were saved, show success message
            if edited:
                self.refresh_product_table()
                QtWidgets.QMessageBox.information(self, "Success", "Product information updated successfully!")

            return edited

        except Exception as e:
            print(f"Error updating products: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to update products: {e}")
            return False

    def delete_product(self):
        self.connect_to_database()
        
        selected_rows = self.ui.InventoryTable.selectionModel().selectedRows()
        
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a row to delete.")
            return
        
        reply = QtWidgets.QMessageBox.question(self, 'Confirm Deletion', 
                    'Are you sure you want to delete selected row(s)?',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                for row in selected_rows:
                    product_id = self.ui.InventoryTable.item(row.row(), 0).text()
                    
                    cursor = self.connection.cursor()
                    cursor.execute("DELETE FROM PRODUCT WHERE PRODUCT_ID = %s", (product_id,))
                    self.connection.commit()
                    
                    self.ui.InventoryTable.removeRow(row.row())
                
                QtWidgets.QMessageBox.information(self, "Success", "Product(s) deleted successfully!")
                self.refresh_product_table()  # Refresh the table after deletion
                
            except Exception as e:
                print(f"Error deleting product(s): {e}")
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to delete product(s): {e}")


    def order_page(self):
        self.connect_to_database()
        self.ui.stackedWidget.setCurrentWidget(self.ui.OrderPage)
        self.ui.Order.setStyleSheet("QPushButton{background-color:rgb(223,203,171); border:null; border-radius:null; }")
        self.ui.Inventory.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.ui.Report.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.ui.Supplier.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.orderTableWidget = self.findChild(QtWidgets.QTableWidget, 'OrderTable')
        self.refresh_order_table()

    def add_order(self):
        try:
            self.connect_to_database()
            
            # Create and configure the modal dialog for the order
            order_dialog = QDialog(self)
            order_dialog.setWindowTitle("Create New Order")
            order_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f2f2f2;
                    border-radius: 10px;
                    padding: 20px;
                }
                
                QDialogButtonBox {
                    padding-top: 10px;
                }

                QPushButton {
                    background-color: #C5B08A;
                    color: white;
                    border-radius: 5px;
                    padding: 5px 10px;
                }

                QPushButton:hover {
                    background-color: rgba(244,237,228,200);
                    color: #000000; 
                }

                QLineEdit, QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                    width: 100%;
                    margin-bottom: 10px;
                }

                QLineEdit:focus, QComboBox:focus {
                    border-color: #4CAF50;
                }

                QLabel {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    color: #333333;
                    margin-bottom: 10px;
                    padding-left: 5px;
                }
            """)

            # Create the layout for the order dialog
            layout = QVBoxLayout(order_dialog)
            order_dialog.setFixedSize(500, 600)

            # Create form layout for input fields (grouped by labels and fields)
            form_layout = QFormLayout()

            # Create input fields in the dialog
            self.date_label = QLabel("Order Date:")
            self.calendar = QCalendarWidget(order_dialog)
            self.calendar.setFixedSize(300, 250)
            self.calendar.setGridVisible(True)
            form_layout.addRow(self.date_label, self.calendar)

            self.product_label = QLabel("Product Name:")
            self.product_combobox = QComboBox()

            # Populate the dropdown with product names from the database
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT PRODUCT_ID, PRODUCT_NAME FROM PRODUCT ORDER BY PRODUCT_NAME")
                products = cursor.fetchall()
                if not products:
                    QMessageBox.warning(self, "Error", "No products found in the database.")
                    return

                for product_id, product_name in products:
                    self.product_combobox.addItem(product_name, product_id)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to fetch products: {e}")
                return

            form_layout.addRow(self.product_label, self.product_combobox)

            self.quantity_label = QLabel("Quantity:")
            self.quantity_lineedit = QLineEdit()
            self.quantity_lineedit.setPlaceholderText("Enter quantity")
            form_layout.addRow(self.quantity_label, self.quantity_lineedit)

            self.payment_label = QLabel("Payment Method:")
            self.payment_combobox = QComboBox()
            self.payment_combobox.addItems(["Cash On Delivery", "Bank Transfer", "GCash"])
            form_layout.addRow(self.payment_label, self.payment_combobox)

            # Add form layout to the main layout
            layout.addLayout(form_layout)

            # Add buttons for accept and reject
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, order_dialog)
            layout.addWidget(buttons)

            def on_accept():
                # Get selected order date
                selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                try:
                    # Validate the order date
                    order_date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
                    if order_date_obj > datetime.now():
                        QMessageBox.warning(order_dialog, "Error", "Order Date cannot be in the future.")
                        return
                except ValueError as e:
                    QMessageBox.warning(order_dialog, "Error", "Invalid date format. Please use YYYY-MM-DD.")
                    return

                # Get the selected product ID from the combobox
                product_id = self.product_combobox.currentData()
                product_name = self.product_combobox.currentText()

                if not product_id:
                    QMessageBox.warning(self, "Error", "Please select a valid product.")
                    return

                # Fetch the product price based on the selected product
                try:
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT PRODUCT_PRICE FROM PRODUCT WHERE PRODUCT_ID = %s", (product_id,))
                    product_price = cursor.fetchone()
                    if not product_price:
                        QMessageBox.warning(self, "Error", f"Failed to retrieve price for {product_name}.")
                        return
                    product_price = product_price[0]
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to fetch product price: {e}")
                    return

                # Get the quantity from the line edit and validate it
                quantity_text = self.quantity_lineedit.text()
                try:
                    quantity = int(quantity_text)
                    if quantity <= 0:
                        QMessageBox.warning(self, "Error", "Quantity must be a positive number.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Error", "Invalid quantity. Please enter a valid positive number.")
                    return

                # Get the selected payment method
                payment_method = self.payment_combobox.currentText()

                # Calculate total cost
                total_cost = quantity * product_price

                try:
                    cursor = self.connection.cursor()
                    # Insert the new order into the database
                    cursor.execute("""
                        INSERT INTO ORDERS (ORDER_DATE, ORDER_QUANTITY, ORDER_PAYMENT, ORDER_TOTAL, PRODUCT_ID)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING ORDER_ID
                    """, (selected_date, quantity, payment_method, decimal.Decimal(total_cost), product_id))
                    order_id = cursor.fetchone()[0]

                    # Update the quantity on hand in the inventory
                    cursor.execute("""
                        UPDATE PRODUCT
                        SET PRODUCT_QOH = PRODUCT_QOH - %s
                        WHERE PRODUCT_ID = %s
                    """, (quantity, product_id))

                    self.connection.commit()
                    print(f"Inserted order with ID: {order_id}")

                    # Insert the order details into the QTableWidget
                    row_position = self.orderTableWidget.rowCount()
                    self.orderTableWidget.insertRow(row_position)

                    self.orderTableWidget.setItem(row_position, 0, QTableWidgetItem(selected_date))
                    self.orderTableWidget.setItem(row_position, 1, QTableWidgetItem(str(order_id)))
                    self.orderTableWidget.setItem(row_position, 2, QTableWidgetItem(product_name))
                    self.orderTableWidget.setItem(row_position, 3, QTableWidgetItem(str(quantity)))
                    self.orderTableWidget.setItem(row_position, 4, QTableWidgetItem(str(product_price)))
                    self.orderTableWidget.setItem(row_position, 5, QTableWidgetItem(str(total_cost)))
                    self.orderTableWidget.setItem(row_position, 6, QTableWidgetItem(payment_method))
                    self.refresh_order_table()

                    # Close the dialog after success
                    order_dialog.accept()

                except Exception as e:
                    print(f"Error inserting order: {e}")
                    QMessageBox.warning(order_dialog, "Error", f"Failed to add order: {e}")

            buttons.accepted.connect(on_accept)
            buttons.rejected.connect(order_dialog.reject)

            # Show the modal dialog
            order_dialog.exec_()

        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def toggle_edit_mode_order(self):
        if self.Editordbutton.text() == "Save":
            if self.save_edited_order_data():  # Save changes and check if successful
                self.Editordbutton.setText("Edit")
                for row in range(self.orderTableWidget.rowCount()):
                    for col in range(self.orderTableWidget.columnCount()):
                        item = self.orderTableWidget.item(row, col)
                        if item:
                            # Disable editing for all columns
                            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        else:  # If the text is "Edit"
            self.Editordbutton.setText("Save")
            for row in range(self.orderTableWidget.rowCount()):
                for col in range(self.orderTableWidget.columnCount()):
                    item = self.orderTableWidget.item(row, col)
                    if item:
                        # Enable editing for quantity and payment method columns
                        if col == 3 or col == 6:
                            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)



    def save_edited_order_data(self):
        self.connect_to_database()
        try:
            edited = False  # Flag to track if any changes were saved
            for row in range(self.orderTableWidget.rowCount()):
                order_id = self.orderTableWidget.item(row, 1).text()
                quantity = self.orderTableWidget.item(row, 3).text()
                payment_method = self.orderTableWidget.item(row, 6).text()

                # Fetch the product price from the corresponding product
                product_name = self.orderTableWidget.item(row, 2).text()
                product_price = self.get_product_price(product_name)
                if product_price is None:
                    QtWidgets.QMessageBox.warning(self, "Error", f"Failed to retrieve price for {product_name}.")
                    continue

                # Calculate the new total cost
                total_cost = float(quantity) * float(product_price)

                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE ORDERS
                    SET ORDER_QUANTITY = %s, ORDER_PAYMENT = %s, ORDER_TOTAL = %s
                    WHERE ORDER_ID = %s
                """, (quantity, payment_method, decimal.Decimal(total_cost), order_id))
                self.connection.commit()

                # Check if any changes were actually made and saved
                if cursor.rowcount > 0:
                    edited = True

                    # Update the total cost in the QTableWidget
                    self.orderTableWidget.setItem(row, 5, QTableWidgetItem(str(total_cost)))

            # If any changes were saved, show success message
            if edited:
                self.refresh_order_table()
                QtWidgets.QMessageBox.information(self, "Success", "Order information updated successfully!")

            return edited

        except Exception as e:
            print(f"Error updating orders: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to update orders: {e}")
            return False

    def delete_order(self):
        self.connect_to_database()
        
        selected_rows = self.orderTableWidget.selectionModel().selectedRows()
        
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a row to delete.")
            return
        
        reply = QtWidgets.QMessageBox.question(self, 'Confirm Deletion', 
                    'Are you sure you want to delete selected row(s)?',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                for row in selected_rows:
                    order_id = self.orderTableWidget.item(row.row(), 1).text()
                    
                    cursor = self.connection.cursor()
                    cursor.execute("DELETE FROM ORDERS WHERE ORDER_ID = %s", (order_id,))
                    self.connection.commit()
                    
                    self.orderTableWidget.removeRow(row.row())
                
                QtWidgets.QMessageBox.information(self, "Success", "Order(s) deleted successfully!")
                self.refresh_order_table()  # Refresh the table after deletion
                
            except Exception as e:
                print(f"Error deleting order(s): {e}")
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to delete order(s): {e}")

    def refresh_order_table(self):
        try:
            self.ui.Order.setStyleSheet("QPushButton{background-color:rgb(223,203,171); border:null; border-radius:null; }")
            self.ui.Inventory.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
            self.ui.Report.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
            self.ui.Supplier.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
    
            # Ensure a valid database connection
            if not self.connection:
                raise Exception("Database connection is not established.")

            # Fetch orders from the database
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT O.ORDER_DATE, O.ORDER_ID, P.PRODUCT_NAME, O.ORDER_QUANTITY, P.PRODUCT_PRICE, 
                    O.ORDER_TOTAL, O.ORDER_PAYMENT
                FROM ORDERS O
                INNER JOIN PRODUCT P ON O.PRODUCT_ID = P.PRODUCT_ID
            """)
            orders = cursor.fetchall()
            print(f"Orders fetched: {orders}")  # Debugging

            # Clear and update the table
            self.ui.OrderTable.setRowCount(0)  # Clear existing rows
            self.ui.OrderTable.setColumnCount(7)
            self.ui.OrderTable.setHorizontalHeaderLabels(
                ["Order Date", "Order ID", "Product Name", "Quantity", "Price", "Total", "Payment"]
            )

            for row_number, row_data in enumerate(orders):
                self.ui.OrderTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    if column_number in (3, 6):  # Editable columns
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    self.ui.OrderTable.setItem(row_number, column_number, item)

            print("Order table refreshed successfully.")

        except Exception as e:
            print(f"Error fetching orders: {e}")
            import traceback
            traceback.print_exc()


    def get_product_names(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT PRODUCT_NAME FROM PRODUCT")
            products = cursor.fetchall()
            product_names = [product[0] for product in products]
            return product_names
        except Exception as e:
            print(f"Error fetching product names: {e}")
            return []

    def get_product_price(self, product_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT PRODUCT_PRICE FROM PRODUCT WHERE PRODUCT_NAME = %s", (product_name,))
            price = cursor.fetchone()
            if price:
                return price[0]
            else:
                return None
        except Exception as e:
            print(f"Error fetching product price: {e}")
            return None



    def CSR_page(self):
        try:
            self.connect_to_database()
            self.ui.stackedWidget.setCurrentWidget(self.ui.SalesReportPage)
            self.ui.Report.setStyleSheet("QPushButton { background-color: rgb(223, 203, 171); border: none; border-radius: none; }")
            self.ui.Inventory.setStyleSheet("QPushButton { background-color: none; border: none; } QPushButton:hover { background-color: rgba(255, 255, 255, 50); border-radius: 5px; }")
            self.ui.Order.setStyleSheet("QPushButton { background-color: none; border: none; } QPushButton:hover { background-color: rgba(255, 255, 255, 50); border-radius: 5px; }")
            self.ui.Supplier.setStyleSheet("QPushButton { background-color: none; border: none; } QPushButton:hover { background-color: rgba(255, 255, 255, 50); border-radius: 5px; }")

            # SQL query to fetch sales report data
            query = """
            SELECT 
                SR.SALES_REPORT_ID, 
                SR.SALES_DATE, 
                O.ORDER_ID, 
                P.PRODUCT_NAME, 
                S.SUPP_NAME, 
                SUM(O.ORDER_TOTAL) AS TOTAL_SALES, 
                O.ORDER_PAYMENT 
            FROM 
                SALES_REPORT SR
            JOIN 
                PRODUCT P ON SR.PRODUCT_ID = P.PRODUCT_ID
            JOIN 
                SUPPLIER S ON SR.SUPP_ID = S.SUPP_ID
            JOIN 
                ORDERS O ON SR.ORDER_ID = O.ORDER_ID
            GROUP BY 
                SR.SALES_REPORT_ID, SR.SALES_DATE, O.ORDER_ID, P.PRODUCT_NAME, S.SUPP_NAME, O.ORDER_PAYMENT
            """

            # Execute the query
            self.cursor.execute(query)
            sales_reports = self.cursor.fetchall()

            # Update SalesReportTable with fetched data
            self.ui.SalesReportTable.setRowCount(len(sales_reports))
            self.ui.SalesReportTable.setColumnCount(7)
            self.ui.SalesReportTable.setHorizontalHeaderLabels(
                ["Sales Report No.", "Date", "Order ID", "Product", "Supplier Name", "Total Spend", "Payment Method"]
            )

            for row_idx, report in enumerate(sales_reports):
                for col_idx, data in enumerate(report):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Make columns uneditable
                    self.ui.SalesReportTable.setItem(row_idx, col_idx, item)

            print("Sales report data loaded successfully.")

        except Exception as e:
            print(f"Error fetching sales reports: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to fetch sales reports: {e}")


    def supplier_page(self):
        self.connect_to_database()
        self.ui.stackedWidget.setCurrentWidget(self.ui.SupplierManagementPage)
        self.ui.Supplier.setStyleSheet("QPushButton{background-color:rgb(223,203,171); border:null; border-radius:null; }")
        self.ui.Inventory.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.ui.Order.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.ui.Report.setStyleSheet("QPushButton{background-color: none; border:null} QPushButton:hover{background-color: rgba(255,255,255,50); border-radius: 5px;}")
        self.supplierTableWidget = self.findChild(QtWidgets.QTableWidget, 'SupplierManagementTable')
        self.refresh_supplier_table()

    def add_supplier(self):
        self.connect_to_database()

        # Create a modal dialog for supplier input
        supplier_dialog = QDialog(self)
        supplier_dialog.setWindowTitle("Add Supplier")
        supplier_dialog.setStyleSheet("""
            QDialog {
                background-color: #f2f2f2;
                border-radius: 10px;
                padding: 20px;
            }
            QDialogButtonBox {
                padding-top: 10px;
            }
            QPushButton {
                background-color: #C5B08A;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(244,237,228,200);
                color: #000000; 
            }
                                      /* Adjust the size of the input fields */
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                max-width: 350px; /* Adjust width as needed */
                margin-bottom: 10px;
                height: 30px;
            }

            QLineEdit:focus {
                border-color: #4CAF50; /* Green border on focus */
            }
             QLabel {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    color: #333333;
                    margin-bottom: 10px;
                    padding-left: 5px;
                }
            QLineEdit[placeholder] {
                color: #888888; /* Lighter color for placeholder text */
            }
        """)
    
        # Set the dialog size
        supplier_dialog.setFixedSize(450, 325)

        # Layout for the dialog
        layout = QVBoxLayout(supplier_dialog)

        # Form layout to add fields
        form_layout = QFormLayout()

        # Supplier Name
        supplier_name_input = QLineEdit(supplier_dialog)
        form_layout.addRow("Supplier Name:", supplier_name_input)

        # Supplier Email
        supplier_email_input = QLineEdit(supplier_dialog)
        form_layout.addRow("Supplier Email:", supplier_email_input)

        # Supplier Contact Info
        supplier_contact_input = QLineEdit(supplier_dialog)
        form_layout.addRow("Supplier Contact Info:", supplier_contact_input)

        # Add form layout to the dialog layout
        layout.addLayout(form_layout)

        # Button box for Ok and Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, supplier_dialog)
        layout.addWidget(buttons)

        # Handle Ok button click
        def on_ok_clicked():
            supplier_name = supplier_name_input.text()
            supplier_email = supplier_email_input.text()
            supplier_contact = supplier_contact_input.text()

            # Validate the input fields
            if not supplier_name or not supplier_email or not supplier_contact:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "All fields must be filled out.")
                return

            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, supplier_email):
                QtWidgets.QMessageBox.warning(self, "Invalid Email Address", "Please enter a valid email address.")
                return

            # Validate phone number format
            phone_pattern = r'^(09\d{9}|\+639\d{9})$'
            if not re.match(phone_pattern, supplier_contact):
                QtWidgets.QMessageBox.warning(self, "Invalid Phone Number", "Phone number must be either 11 digits starting with '09' or start with '+63' followed by 9 digits.")
                return

            try:
                cursor = self.connection.cursor()
                # Check if the supplier name already exists (case-insensitive)
                cursor.execute("SELECT SUPP_NAME FROM SUPPLIER WHERE SUPP_NAME ILIKE %s", (supplier_name,))
                existing_supplier = cursor.fetchone()

                if existing_supplier:
                    QtWidgets.QMessageBox.warning(self, "Duplicate Supplier", "A supplier with this name already exists. Please enter a different name.")
                    return

                # Insert into the database
                cursor.execute("""
                    INSERT INTO SUPPLIER (SUPP_NAME, SUPP_EMAIL, SUPP_CONTACT)
                    VALUES (%s, %s, %s) RETURNING SUPP_ID
                """, (supplier_name, supplier_email, supplier_contact))
                supp_id = cursor.fetchone()[0]
                self.connection.commit()

                # Insert into the QTableWidget
                row_position = self.supplierTableWidget.rowCount()
                self.supplierTableWidget.insertRow(row_position)

                self.supplierTableWidget.setItem(row_position, 0, QTableWidgetItem(str(supp_id)))
                self.supplierTableWidget.setItem(row_position, 1, QTableWidgetItem(supplier_name))
                self.supplierTableWidget.setItem(row_position, 2, QTableWidgetItem(supplier_email))
                self.supplierTableWidget.setItem(row_position, 3, QTableWidgetItem(supplier_contact))

                self.refresh_supplier_table()

                # Close the dialog after successful insertion
                supplier_dialog.accept()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        # Handle Cancel button click
        def on_cancel_clicked():
            supplier_dialog.reject()  # Close the dialog without making any changes

        # Connect the buttons to the handler functions
        buttons.accepted.connect(on_ok_clicked)
        buttons.rejected.connect(on_cancel_clicked)

        # Show the modal dialog
        supplier_dialog.exec_()

           
    def refresh_supplier_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT SUPP_ID, SUPP_NAME, SUPP_EMAIL, SUPP_CONTACT FROM SUPPLIER")
            suppliers = cursor.fetchall()

            self.ui.SupplierManagementTable.setRowCount(0)  # Clear the table
            for row_number, row_data in enumerate(suppliers):
                self.ui.SupplierManagementTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ui.SupplierManagementTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        except Exception as e:
            print(f"Error fetching suppliers: {e}")

    def toggle_edit_mode_supplier(self):
        if self.Editsuppbutton.text() == "Save":
            if self.save_edited_supplier_data():  # Save changes and check if successful
                self.Editsuppbutton.setText("Edit")
                for row in range(self.supplierTableWidget.rowCount()):
                    for col in range(self.supplierTableWidget.columnCount()):
                        item = self.supplierTableWidget.item(row, col)
                        if item:
                            # Disable editing for all columns
                            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        else:  # If the text is "Edit"
            self.Editsuppbutton.setText("Save")
            for row in range(self.supplierTableWidget.rowCount()):
                for col in range(self.supplierTableWidget.columnCount()):
                    item = self.supplierTableWidget.item(row, col)
                    if item:
                        # Enable editing for all columns
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

    def save_edited_supplier_data(self):
        self.connect_to_database()
        try:
            edited = False  # Flag to track if any changes were saved
            for row in range(self.supplierTableWidget.rowCount()):
                supp_id = self.supplierTableWidget.item(row, 0).text()
                supplier_name = self.supplierTableWidget.item(row, 1).text()
                supplier_email = self.supplierTableWidget.item(row, 2).text()
                supplier_contact = self.supplierTableWidget.item(row, 3).text()

                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE SUPPLIER
                    SET SUPP_NAME = %s, SUPP_EMAIL = %s, SUPP_CONTACT = %s
                    WHERE SUPP_ID = %s
                """, (supplier_name, supplier_email, supplier_contact, supp_id))
                self.connection.commit()

                # Check if any changes were actually made and saved
                if cursor.rowcount > 0:
                    edited = True
            
            # If any changes were saved, show success message
            if edited:
                self.refresh_supplier_table()
                QtWidgets.QMessageBox.information(self, "Success", "Supplier information updated successfully!")
            
            return edited

        except Exception as e:
            print(f"Error updating suppliers: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to update suppliers: {e}")
            return False

    def delete_supplier(self):
        self.connect_to_database()

        try:
            # Ensure the table widget exists
            if not hasattr(self.ui, 'SupplierManagementTable'):
                QtWidgets.QMessageBox.critical(self, "Error", "Supplier table widget not found!")
                return

            selected_rows = self.ui.SupplierManagementTable.selectionModel().selectedRows()

            if not selected_rows:
                QtWidgets.QMessageBox.warning(self, "Error", "Please select a row to delete.")
                return

            reply = QtWidgets.QMessageBox.question(
                self, 'Confirm Deletion', 
                'Are you sure you want to delete selected row(s)?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.Yes:
                for row in selected_rows:
                    supp_id = self.ui.SupplierManagementTable.item(row.row(), 0).text()
                    
                    cursor = self.connection.cursor()
                    cursor.execute("DELETE FROM SUPPLIER WHERE SUPP_ID = %s", (supp_id,))
                    self.connection.commit()

                    self.ui.SupplierManagementTable.removeRow(row.row())

                QtWidgets.QMessageBox.information(self, "Success", "Supplier(s) deleted successfully!")
                self.refresh_supplier_table()  # Refresh the table after deletion

        except AttributeError as ae:
            QtWidgets.QMessageBox.critical(self, "Error", f"Attribute error: {ae}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    
 
    # Log out
    def logout(self):
     # Show confirmation dialog before closing the window
        reply = QtWidgets.QMessageBox.question(self, 'Confirm Logout', 
                                           'Are you sure you want to logout?', 
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                           QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            print("Logged out!")
            self.close()  # Close the main window
            self.login_window = MainWindow()  # Create a new instance of the login window
            self.login_window.show()  # Show the login window
        else:
            print("Logout cancelled.")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    login_window = MainWindow()
    sys.exit(app.exec_())


