import serial
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import json
import os
from tkinter.font import Font
from typing import Optional

class ModernTheme:
    def __init__(self):
        self.dark = {
            'bg': '#1c1c1e',
            'fg': '#ffffff',
            'accent': '#0a84ff',
            'secondary_bg': '#2c2c2e',
            'border': '#3a3a3c',
            'error': '#ff453a',
            'success': '#32d74b'
        }
        self.light = {
            'bg': '#f2f2f7',
            'fg': '#000000',
            'accent': '#007aff',
            'secondary_bg': '#ffffff',
            'border': '#c6c6c8',
            'error': '#ff3b30',
            'success': '#34c759'
        }
        self.current = self.dark

    def toggle(self):
        self.current = self.light if self.current == self.dark else self.dark
        return self.current

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            relief=tk.FLAT,
            borderwidth=0,
            padx=16,
            pady=8,
            font=('SF Pro Text', 13),
            cursor='hand2'
        )
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self['background'] = self.theme['accent']
        self['foreground'] = '#ffffff'

    def on_leave(self, e):
        self['background'] = self.theme['secondary_bg']
        self['foreground'] = self.theme['accent']

class ModernTable(ttk.Treeview):
    def __init__(self, master, theme, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        style = ttk.Style()
        
        # Configure Treeview colors
        style.configure(
            "Custom.Treeview",
            background=theme['secondary_bg'],
            foreground=theme['fg'],
            fieldbackground=theme['secondary_bg'],
            borderwidth=0
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=theme['secondary_bg'],
            foreground=theme['fg'],
            borderwidth=0,
            font=('SF Pro Text', 12, 'bold')
        )
        self.configure(style="Custom.Treeview")

class RFIDApp:
    def __init__(self, root):
        self.root = root
        self.theme = ModernTheme()
        self.setup_window()
        self.load_user_data()
        self.setup_ui()
        self.serial_port: Optional[serial.Serial] = None
        self.is_logging = False

    def setup_window(self):
        self.root.title("RFID Logger")
        self.root.geometry("800x600")
        self.root.configure(bg=self.theme.current['bg'])
        self.root.option_add('*Font', 'Helvetica')

    def setup_ui(self):
        # Main container
        self.main_container = tk.Frame(
            self.root,
            bg=self.theme.current['bg'],
            padx=20,
            pady=20
        )
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header = tk.Frame(
            self.main_container,
            bg=self.theme.current['bg']
        )
        self.header.pack(fill=tk.X, pady=(0, 20))

        # Title and theme toggle
        self.title_label = tk.Label(
            self.header,
            text="RFID Logger",
            font=('SF Pro Display', 24, 'bold'),
            bg=self.theme.current['bg'],
            fg=self.theme.current['fg']
        )
        self.title_label.pack(side=tk.LEFT)

        self.theme_button = ModernButton(
            self.header,
            text="Toggle Theme",
            command=self.toggle_theme,
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['accent']
        )
        self.theme_button.pack(side=tk.RIGHT)

        # Status section
        self.status_frame = tk.Frame(
            self.main_container,
            bg=self.theme.current['secondary_bg'],
            padx=16,
            pady=16
        )
        self.status_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_label = tk.Label(
            self.status_frame,
            text="Status: Waiting for RFID Scan",
            font=('Helvetica', 14),
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['fg']
        )
        self.status_label.pack(side=tk.LEFT)

        # Control buttons
        self.button_frame = tk.Frame(
            self.main_container,
            bg=self.theme.current['bg']
        )
        self.button_frame.pack(fill=tk.X, pady=(0, 20))

        self.start_button = ModernButton(
            self.button_frame,
            text="Start Logging",
            command=self.start_logging,
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['accent']
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ModernButton(
            self.button_frame,
            text="Stop Logging",
            command=self.stop_logging,
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['accent']
        )
        self.stop_button.pack(side=tk.LEFT)

        # User management buttons
        self.user_button_frame = tk.Frame(
            self.main_container,
            bg=self.theme.current['bg']
        )
        self.user_button_frame.pack(fill=tk.X, pady=(0, 20))

        for text, command in [
            ("Add User", self.add_user),
            ("Remove User", self.remove_user),
            ("Rename User", self.rename_user)
        ]:
            btn = ModernButton(
                self.user_button_frame,
                text=text,
                command=command,
                bg=self.theme.current['secondary_bg'],
                fg=self.theme.current['accent']
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))

        # Table
        self.setup_table()

    def setup_table(self):
        columns = ("Label", "Date", "Time", "Card UID", "RFID UID")
        self.tree = ModernTable(
            self.main_container,
            self.theme.current,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def toggle_theme(self):
        new_theme = self.theme.toggle()
        self.root.configure(bg=new_theme['bg'])
        self.main_container.configure(bg=new_theme['bg'])
        self.header.configure(bg=new_theme['bg'])
        self.title_label.configure(
            bg=new_theme['bg'],
            fg=new_theme['fg']
        )
        self.status_frame.configure(bg=new_theme['secondary_bg'])
        self.status_label.configure(
            bg=new_theme['secondary_bg'],
            fg=new_theme['fg']
        )
        self.button_frame.configure(bg=new_theme['bg'])
        self.user_button_frame.configure(bg=new_theme['bg'])

        # Update all buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, ModernButton):
                widget.configure(
                    bg=new_theme['secondary_bg'],
                    fg=new_theme['accent']
                )

        # Update table
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background=new_theme['secondary_bg'],
            foreground=new_theme['fg'],
            fieldbackground=new_theme['secondary_bg']
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=new_theme['secondary_bg'],
            foreground=new_theme['fg']
        )

    # The rest of the methods remain the same as in your original code
    def load_user_data(self):
        self.card_names = {}
        if os.path.exists('user_data.json'):
            with open('user_data.json', 'r') as f:
                self.card_names = json.load(f)

    def save_user_data(self):
        with open('user_data.json', 'w') as f:
            json.dump(self.card_names, f)

    def start_logging(self):
        self.is_logging = True
        self.status_label.config(text="Status: Logging RFID Data...")
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)
            self.serial_thread = threading.Thread(target=self.read_serial_data)
            self.serial_thread.daemon = True
            self.serial_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to serial port: {str(e)}")
            self.is_logging = False

    def stop_logging(self):
        self.is_logging = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.status_label.config(text="Status: Logging Stopped")

    def read_serial_data(self):
        while self.is_logging:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode().strip()
                if data.startswith("DATA"):
                    parts = data.split(',')
                    if len(parts) == 5:
                        label, date, time, rfid_uid = parts[1], parts[2], parts[3], parts[4]
                        current_time = datetime.now().strftime("%H:%M")
                        
                        if rfid_uid not in self.card_names:
                            self.ask_for_name(rfid_uid)
                        else:
                            label = self.card_names[rfid_uid]
                        
                        self.log_to_table(label, date, current_time, rfid_uid)
                        self.status_label.config(text=f"Status: {label} scanned at {current_time}")

    def create_modal_window(self, title, width=400, height=250):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.configure(bg=self.theme.current['bg'])
        window.transient(self.root)
        window.grab_set()
        
        # Center the window
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        return window

    def ask_for_name(self, rfid_uid):
        window = self.create_modal_window("Enter Name")
        
        frame = tk.Frame(window, bg=self.theme.current['bg'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(
            frame,
            text="Enter Name for this Card:",
            font=('Helvetica', 14),
            bg=self.theme.current['bg'],
            fg=self.theme.current['fg']
        )
        label.pack(pady=(0, 10))
        
        entry = tk.Entry(
            frame,
            font=('Helvetica', 13),
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['fg'],
            insertbackground=self.theme.current['fg']
        )
        entry.pack(fill=tk.X, pady=(0, 20))
        
        def save_name():
            name = entry.get()
            if name:
                self.card_names[rfid_uid] = name
                self.save_user_data()
                window.destroy()
            else:
                messagebox.showerror("Error", "Name cannot be empty!")
        
        save_btn = ModernButton(
            frame,
            text="Save",
            command=save_name,
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['accent']
        )
        save_btn.pack()

    def add_user(self):
        self.ask_for_name("new_card_uid")

    def remove_user(self):
        window = self.create_modal_window("Remove User")
        
        frame = tk.Frame(window, bg=self.theme.current['bg'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(
            frame,
            text="Enter Card UID to Remove:",
            font=('SF Pro Text', 14),
            bg=self.theme.current['bg'],
            fg=self.theme.current['fg']
        )
        label.pack(pady=(0, 10))
        
        entry = tk.Entry(
            frame,
            font=('Helvetica', 13),
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['fg'],
            insertbackground=self.theme.current['fg']
        )
        entry.pack(fill=tk.X, pady=(0, 20))
        
        def remove():
            uid = entry.get()
            if uid in self.card_names:
                del self.card_names[uid]
                self.save_user_data()
                messagebox.showinfo("Success", f"User with card ID {uid} removed successfully.")
                window.destroy()
                self.update_user_table()
            else:
                messagebox.showerror("Error", "Card ID not found.")
        
        remove_btn = ModernButton(
            frame,
            text="Remove",
            command=remove,
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['accent']
        )
        remove_btn.pack()

    def rename_user(self):
        window = self.create_modal_window("Rename User")
        
        frame = tk.Frame(window, bg=self.theme.current['bg'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Card UID input
        uid_label = tk.Label(
            frame,
            text="Enter Card UID:",
            font=('SF Pro Text', 14),
            bg=self.theme.current['bg'],
            fg=self.theme.current['fg']
        )
        uid_label.pack(pady=(0, 5))
        
        uid_entry = tk.Entry(
            frame,
            font=('SF Pro Text', 13),
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['fg'],
            insertbackground=self.theme.current['fg']
        )
        uid_entry.pack(fill=tk.X, pady=(0, 15))
        
        # New name input
        name_label = tk.Label(
            frame,
            text="Enter New Name:",
            font=('SF Pro Text', 14),
            bg=self.theme.current['bg'],
            fg=self.theme.current['fg']
        )
        name_label.pack(pady=(0, 5))
        
        name_entry = tk.Entry(
            frame,
            font=('SF Pro Text', 13),
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['fg'],
            insertbackground=self.theme.current['fg']
        )
        name_entry.pack(fill=tk.X, pady=(0, 20))
        
        def rename():
            uid = uid_entry.get()
            new_name = name_entry.get()
            if uid in self.card_names:
                self.card_names[uid] = new_name
                self.save_user_data()
                messagebox.showinfo("Success", f"User with card ID {uid} renamed successfully.")
                window.destroy()
                self.update_user_table()
            else:
                messagebox.showerror("Error", "Card ID not found.")
        
        rename_btn = ModernButton(
            frame,
            text="Rename",
            command=rename,
            bg=self.theme.current['secondary_bg'],
            fg=self.theme.current['accent']
        )
        rename_btn.pack()

    def log_to_table(self, label, date, time, rfid_uid):
        self.tree.insert("", "end", values=(label, date, time, rfid_uid, rfid_uid))

    def update_user_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for uid, name in self.card_names.items():
            self.tree.insert("", "end", values=(name, "N/A", "N/A", uid, uid))

    def exit_app(self):
        if self.is_logging and self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = RFIDApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
