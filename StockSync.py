import tkinter as tk
from tkinter import messagebox

#Checking the username and password
def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" and password == "":
        messagebox.showinfo("Login info", "Logged in successfully")
    else:
        messagebox.showinfo("Login info", "Invalid credentials")
    
    #Popup message
    messagebox.showinfo("Login info", "Logged in successfully")

# Create the main window
root = tk.Tk()
root.title("StockSync Inventory Management")

# Create a label and entry for the username
username_label = tk.Label(root, text="Username")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

# Create a label and entry for the password
password_label = tk.Label(root, text="Password")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

# Create a login button
login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

# Run the GUI
root.mainloop()
