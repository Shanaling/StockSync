#Import necessary modules:
import tkinter as tk
import mysql.connector
from tkinter import messagebox, ttk, PhotoImage
from PIL import Image, ImageTk  #Import from Pillow to handle image operations

class ToolTip:
    """
    A class to create a tooltip that appears when hovering over a widget.
    """
    def __init__(self, widget, text='info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        #Bind mouse events to show and hide the tooltip:
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event):
        "Display text in tooltip window"
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        
        #Creates a toplevel window:
        self.tipwindow = tk.Toplevel(self.widget)
        
        #Leaves only the label and removes the app window:
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        """
        Destroy the tooltip window.
        """
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

#Main application class definition:
class Application(tk.Frame):
    """
    The main application class, containing the GUI and functionality.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        # Connect to the database
        self.connect_to_mysql()
        # Create the database and table
        self.create_database()

       # Load, resize, and display the inventory2_icon.png in the upper left corner
        inventory2_icon_original = Image.open("inventory2_icon.png")
        inventory2_icon_resized = inventory2_icon_original.resize((40, 40), Image.Resampling.LANCZOS)  # Resize to same size as inventory_icon
        self.inventory2_icon = ImageTk.PhotoImage(inventory2_icon_resized)
        self.inventory2_icon_label = tk.Label(self.master, image=self.inventory2_icon)
        self.inventory2_icon_label.pack(anchor='nw')  # 'nw' = North West or upper left

        ToolTip(self.inventory2_icon_label, "A stack of boxes with a clipboard in front")

    def create_widgets(self):
        """
        Creates the widgets for the main window.
        """

        # Main Window Introduction Label
        self.intro_label = tk.Label(self, text="Manage With StockSync", font=("Helvetica", 12))
        self.intro_label.pack(side="top", pady=(10,20))  # Add some padding for better spacing

        #Connect to MySQL button
        self.connect_button = tk.Button(self)
        self.connect_button["text"] = "Connect to MySQL"
        self.connect_button["command"] = self.connect_to_mysql
        self.connect_button.pack(side="top")

        # Description Label for 'View Inventory' button
        self.view_inv_desc_label = tk.Label(self, text="Open the inventory viewing window", font=("Helvetica", 10))
        self.view_inv_desc_label.pack(side="top", pady=(5,0))

        self.view_inventory_button = tk.Button(self, text="View Inventory", command=self.open_inventory_window)
        self.view_inventory_button.pack()

    def connect_to_mysql(self):
        try:
            self.cnx = mysql.connector.connect(user='', password='', host='localhost',database='test') #Add your MYSQL 'user', 'password', and 'host' data
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")

    def open_inventory_window(self):
        self.inventory_window = tk.Toplevel(self.master)
        self.inventory_window.title("Inventory")
        self.inventory_window.geometry("600x400")  # Set the size of the window

        # Inventory Window Introduction Label
        self.inv_window_intro_label = tk.Label(self.inventory_window, text="Current Inventory", font=("Helvetica", 10))
        self.inv_window_intro_label.pack(side="top", pady=(5,10))

        #Load and resize the inventory icon image for the inventory window
        inventory_icon_original = Image.open("inventory_icon.png")
        inventory_icon_resized = inventory_icon_original.resize((40, 40), Image.Resampling.LANCZOS)
        self.inventory_icon = ImageTk.PhotoImage(inventory_icon_resized)

        # Insert the inventory icon image on the upper left side
        self.inventory_icon_label = tk.Label(self.inventory_window, image=self.inventory_icon)
        self.inventory_icon_label.pack(side="top", anchor="nw")

        # Execute the query
        self.cursor.execute("SELECT * FROM inventory")

        # Fetch all the rows
        rows = self.cursor.fetchall()

        # Create a treeview widget
        self.tree = ttk.Treeview(self.inventory_window)
        self.tree["columns"] = ("ID", "Item Name", "Quantity")

        # Define the column
        self.tree.column("#0", width=0, stretch="NO")
        self.tree.column("ID", anchor="w", width=100)
        self.tree.column("Item Name", anchor="w", width=200)
        self.tree.column("Quantity", anchor="w", width=100)

        # Define the headings
        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("ID", text="ID", anchor="w")
        self.tree.heading("Item Name", text="Item Name", anchor="w")
        self.tree.heading("Quantity", text="Quantity", anchor="w")

        # Insert the fetched rows into the treeview widget
        for row in rows:
            self.tree.insert("", "end", values=row)

        # Pack the treeview widget
        self.tree.pack()

        #Buttons
        self.add_item_button = tk.Button(self.inventory_window, text="Add Item", command=self.add_item_window)
        self.add_item_button.pack()

        self.update_item_button = tk.Button(self.inventory_window, text="Update Item", command=self.update_item_window)
        self.update_item_button.pack()

        # Button to delete an item
        self.delete_item_button = tk.Button(self.inventory_window, text="Delete Item", command=self.delete_item_from_inventory)
        self.delete_item_button.pack()

    def delete_item_from_inventory(self):
        selected_item = self.tree.selection()
        if selected_item:  # Check if something is selected
            item_id = self.tree.item(selected_item)['values'][0]
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
            if confirm:
                try:
                    self.cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
                    self.cnx.commit()
                    self.tree.delete(selected_item)  # Remove the item from the Treeview
                    messagebox.showinfo("Success", "Item deleted successfully.")
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Failed to delete item: {err}")
            else:
                messagebox.showwarning("Selection needed", "Please select an item to delete.")    

    def connect_to_mysql(self):
        try:
        # Attempt to connect to the MySQL server (adjust parameters as needed)
            self.cnx = mysql.connector.connect(user='', password='', host='localhost') #Add your MYSQL 'user', 'password', and 'host' data
            self.cursor = self.cnx.cursor()
        # Once connected, try to create the database
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS test")
            self.cnx.commit()  # Commit the changes to make sure the database is created
        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")

    def create_database(self):
        try:
            self.cnx = mysql.connector.connect(user='', password='', host='localhost') #Add your MYSQL 'user', 'password', and 'host' data
            self.cursor = self.cnx.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS test")
            self.cnx.database = 'test'  # Select the 'test' database
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_name VARCHAR(40) NOT NULL,
                    quantity INT NOT NULL
                )
            """)
        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")
    
    #Displays the buttons under the table
    def add_item_window(self):
        print("Add Item button clicked!")

        self.new_item_window = tk.Toplevel(self.master)
        self.new_item_window.title("Add New Item")

        # Label and entry for the item name
        self.item_name_label = tk.Label(self.new_item_window, text="Item Name:")
        self.item_name_label.pack(side="top", anchor="w")
        self.item_name_entry = tk.Entry(self.new_item_window)
        self.item_name_entry.pack()

        # Label and entry for the quantity
        self.quantity_label = tk.Label(self.new_item_window, text="Quantity:")
        self.quantity_label.pack(side="top", anchor="w")
        self.quantity_entry = tk.Entry(self.new_item_window)
        self.quantity_entry.pack()

        # Create an "Add" button
        self.add_button = tk.Button(self.new_item_window, text="Add", command=self.add_item_to_database)
        self.add_button.pack()
        
    def update_item_window(self):
        print("Update Item button clicked!") 

        # Get the selected item from the treeview widget
        selected_item = self.tree.focus()
        item_data = self.tree.item(selected_item)
        item_id = item_data['values'][0]  # Get the ID of the selected item

        # Create a new window
        self.update_window = tk.Toplevel(self.master)
        self.update_window.title("Update Item")

        # Label for the updated item name entry
        self.update_item_name_label = tk.Label(self.update_window, text="Item Name:")
        self.update_item_name_label.pack()
        # Entry for the updated item name
        self.update_item_name_entry = tk.Entry(self.update_window)
        self.update_item_name_entry.pack()

        # Label for the updated quantity entry
        self.update_quantity_label = tk.Label(self.update_window, text="Quantity:")
        self.update_quantity_label.pack()
        # Entry for the updated quantity
        self.update_quantity_entry = tk.Entry(self.update_window)
        self.update_quantity_entry.pack()

        # Prefill the entry fields with existing data
        if item_data['values']:
            self.update_item_name_entry.insert(0, item_data['values'][1])  # Item Name
            self.update_quantity_entry.insert(0, item_data['values'][2])  # Quantity

        # Create an "Update" button
        self.update_button = tk.Button(self.update_window, text="Update", command=lambda: self.update_item_in_database(item_id))
        self.update_button.pack()

    def update_item_in_database(self, item_id):
        # Get the updated item name and quantity from the entries
        updated_item_name = self.update_item_name_entry.get().strip()
        updated_quantity_str = self.update_quantity_entry.get().strip()

        # Validate input
        if not updated_item_name:
            messagebox.showerror("Input Error", "Item name cannot be empty.")
            return
    
        try:
            updated_quantity = int(updated_quantity_str)  # Attempt to convert the string to an integer
        except ValueError:
    # Handles the case where conversion to integer fails (e.g., non-numeric input)
            messagebox.showerror("Input Error", "Please enter a valid integer for quantity.")
            return

# After successfully converting to an integer, check if it is non-negative
        if updated_quantity < 0:
    # Handles the case where the quantity is a number, but it's negative
            messagebox.showerror("Input Error", "Quantity cannot be negative.")
            return

        #Update the item in the database
        try:
            self.cursor.execute("UPDATE inventory SET item_name = %s, quantity = %s WHERE id = %s", (updated_item_name, updated_quantity, item_id))
            self.cnx.commit()
            messagebox.showinfo("Success", "Item updated successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to update item: {err}")
   
    def add_item_to_database(self):
        # Get the item name and quantity from the entries
        item_name = self.item_name_entry.get().strip() # using .strip to remove any leading or trailing whitespace
        quantity_str = self.quantity_entry.get().strip()

        # Check if item name is empty
        if not item_name:
            messagebox.showerror("Input Error", "Item name cannot be empty.")
            return
    # Check if quantity is a valid integer
        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid integer for quantity.")
            return

        # Check if the quantity is non-negative
        if quantity < 0:
            messagebox.showerror("Input Error", "Quantity cannot be negative.")
            return

        # Add the item to the database
        try:
            self.cursor.execute("INSERT INTO inventory (item_name, quantity) VALUES (%s, %s)", (item_name, quantity))
            self.cnx.commit()
            messagebox.showinfo("Success", "Item added successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add item: {err}")         

# Create and run the main window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("StockSync Inventory Management")
    root.geometry("600x400")
    
# Create the database
app = Application(master=root)

# Run the GUI
app.mainloop()
