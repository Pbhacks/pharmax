import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from datetime import datetime
import json
import os

# Path to store user data
USER_DATA_FILE = 'user_data.json'

# Function to handle serial data reading and display in the table
class RFIDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Logger")
        self.root.geometry("600x500")
        self.root.configure(bg="black")

        # Initialize user data dictionary
        self.card_names = {}  # Dictionary to store card IDs and their corresponding names
        self.load_user_data()

        # Set up the UI components
        self.create_top_panel()
        
        self.status_label = tk.Label(self.root, text="Status: Waiting for RFID Scan", font=("Helvetica", 12), fg="gold", bg="black")
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start", font=("Helvetica", 14), fg="black", bg="gold", command=self.start_logging)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", font=("Helvetica", 14), fg="black", bg="gold", command=self.stop_logging)
        self.stop_button.pack(pady=10)

        # Create Treeview table for logging RFID data
        self.columns = ("Label", "Date", "Time", "Card UID", "RFID UID")
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings", height=10)
        self.tree.pack(pady=20)

        for col in self.columns:
            self.tree.heading(col, text=col)

        self.serial_port = None
        self.is_logging = False

    def create_top_panel(self):
        """ Create top panel for managing users (add/remove) """
        top_panel = tk.Frame(self.root, bg="black")
        top_panel.pack(pady=10, fill=tk.X)

        self.add_button = tk.Button(top_panel, text="Add User", font=("Helvetica", 12), fg="black", bg="gold", command=self.add_user)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(top_panel, text="Remove User", font=("Helvetica", 12), fg="black", bg="gold", command=self.remove_user)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.rename_button = tk.Button(top_panel, text="Rename User", font=("Helvetica", 12), fg="black", bg="gold", command=self.rename_user)
        self.rename_button.pack(side=tk.LEFT, padx=5)

    def load_user_data(self):
        """ Load user data from the JSON file """
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                self.card_names = json.load(f)
        else:
            self.card_names = {}

    def save_user_data(self):
        """ Save user data to the JSON file """
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(self.card_names, f)

    def start_logging(self):
        """ Start serial communication and logging to the table """
        self.is_logging = True
        self.status_label.config(text="Status: Logging RFID Data...")
        
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)  # Adjust COM port as needed
            self.serial_thread = threading.Thread(target=self.read_serial_data)
            self.serial_thread.daemon = True
            self.serial_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to serial port: {str(e)}")
            self.is_logging = False

    def stop_logging(self):
        """ Stop serial communication and logging """
        self.is_logging = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.status_label.config(text="Status: Logging Stopped")

    def read_serial_data(self):
        """ Reads serial data and logs it in the table """
        while self.is_logging:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode().strip()
                print(f"Received data: {data}")  # Debugging line to check received data
                if data.startswith("DATA"):
                    # Example data: DATA,Name,YYYY-MM-DD,HH:MM:SS,UID
                    parts = data.split(',')
                    if len(parts) == 5:
                        label, date, time, rfid_uid = parts[1], parts[2], parts[3], parts[4]
                        print(f"Logging data: {label}, {date}, {time}, {rfid_uid}")  # Debugging line for logging

                        # Get the current time in hh:mm format
                        current_time = datetime.now().strftime("%H:%M")

                        # Check if the card ID has been previously scanned
                        if rfid_uid not in self.card_names:
                            self.ask_for_name(rfid_uid)  # Prompt user for a name if this card ID is new
                        else:
                            label = self.card_names[rfid_uid]  # Use the stored name

                        self.log_to_table(label, date, current_time, rfid_uid)
                        self.status_label.config(text=f"Status: {label} scanned at {current_time}")

    def ask_for_name(self, rfid_uid):
        """ Ask the user to input a name for the card """
        def save_name():
            name = name_entry.get()
            if name:
                self.card_names[rfid_uid] = name  # Store the name in the dictionary
                self.save_user_data()  # Save the user data to the file
                name_window.destroy()  # Close the input window
            else:
                messagebox.showerror("Error", "Name cannot be empty!")

        # Create a new window to ask for the name
        name_window = tk.Toplevel(self.root)
        name_window.title("Enter Name")
        name_window.geometry("300x150")
        label = tk.Label(name_window, text="Enter Name for this Card:", font=("Helvetica", 12))
        label.pack(pady=10)

        name_entry = tk.Entry(name_window, font=("Helvetica", 12))
        name_entry.pack(pady=10)

        save_button = tk.Button(name_window, text="Save", font=("Helvetica", 12), command=save_name)
        save_button.pack(pady=10)

    def log_to_table(self, label, date, time, rfid_uid):
        """ Log the scanned RFID data to the Treeview table """
        self.tree.insert("", "end", values=(label, date, time, rfid_uid, rfid_uid))

    def add_user(self):
        """ Add a new user """
        self.ask_for_name("new_card_uid")

    def remove_user(self):
        """ Remove an existing user """
        def remove_user_from_data():
            uid = card_uid_entry.get()
            if uid in self.card_names:
                del self.card_names[uid]
                self.save_user_data()
                messagebox.showinfo("Success", f"User with card ID {uid} removed successfully.")
                remove_window.destroy()
                self.update_user_table()
            else:
                messagebox.showerror("Error", "Card ID not found.")

        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove User")
        remove_window.geometry("300x150")

        label = tk.Label(remove_window, text="Enter Card UID to Remove:", font=("Helvetica", 12))
        label.pack(pady=10)

        card_uid_entry = tk.Entry(remove_window, font=("Helvetica", 12))
        card_uid_entry.pack(pady=10)

        remove_button = tk.Button(remove_window, text="Remove", font=("Helvetica", 12), command=remove_user_from_data)
        remove_button.pack(pady=10)

    def rename_user(self):
        """ Rename an existing user """
        def rename_user_in_data():
            uid = card_uid_entry.get()
            new_name = new_name_entry.get()
            if uid in self.card_names:
                self.card_names[uid] = new_name
                self.save_user_data()
                messagebox.showinfo("Success", f"User with card ID {uid} renamed successfully.")
                rename_window.destroy()
                self.update_user_table()
            else:
                messagebox.showerror("Error", "Card ID not found.")

        rename_window = tk.Toplevel(self.root)
        rename_window.title("Rename User")
        rename_window.geometry("300x200")

        label = tk.Label(rename_window, text="Enter Card UID to Rename:", font=("Helvetica", 12))
        label.pack(pady=5)

        card_uid_entry = tk.Entry(rename_window, font=("Helvetica", 12))
        card_uid_entry.pack(pady=5)

        new_name_label = tk.Label(rename_window, text="Enter New Name:", font=("Helvetica", 12))
        new_name_label.pack(pady=5)

        new_name_entry = tk.Entry(rename_window, font=("Helvetica", 12))
        new_name_entry.pack(pady=5)

        rename_button = tk.Button(rename_window, text="Rename", font=("Helvetica", 12), command=rename_user_in_data)
        rename_button.pack(pady=10)

    def update_user_table(self):
        """ Update the user table """
        for item in self.tree.get_children():
            self.tree.delete(item)
        for uid, name in self.card_names.items():
            self.tree.insert("", "end", values=(name, "N/A", "N/A", uid, uid))

    def exit_app(self):
        """ Safely exit the application """
        if self.is_logging and self.serial_port.is_open:
            self.serial_port.close()
        self.root.quit()

# Set up the main window and application
if __name__ == "__main__":
    root = tk.Tk()
    app = RFIDApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
