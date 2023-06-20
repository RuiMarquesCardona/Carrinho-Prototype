import numpy as np
import requests
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
import sys
import json

# Get screen dimensions
screen_width, screen_height = 1920, 1080  # Change these values to match your screen size

# Create black image to display text
text_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

input_buffer = ''
readCode = ''
input_timestamp = 0

script_path = "C:\LEDProjekt\MultipleLEDs\ScriptEmuMTSMULT.py"
subprocess.Popen(["python3", script_path])

numbers = []
selected_machine = None

checkboxes = []  # List to store checkbox references
checkbox_vars = []

sent_data = {}  # Dictionary to store sent data

def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def check_connection():
    url = 'http://192.168.0.171:5550/api/check_connection'
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
            else:
                subprocess.Popen(["python3", script_path])
        except requests.exceptions.RequestException as e:
            print(f'Error connecting to {url}: {e}')

sent_data_text = None
def clear_positions():
    url = 'http://192.168.0.171:5550/api/clear_positions'
    try:
        response = requests.post(url)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Positions cleared.")
        else:
            messagebox.showerror("Error", "Failed to clear positions.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to clear positions: {str(e)}")
        # Clear sent data and update label
    sent_data.clear()
    if sent_data_text is not None:  # Avoid error when GUI is not initiated yet.
        sent_data_text.delete("1.0", tk.END)

def show_number_selection_screen():
    global numbers
    global selected_machine
    global checkboxes
    global sent_data
    global sent_data_text

    window = tk.Tk()
    window.title("Number Selection")

    sent_data_text = tk.Text(window, width=50, height=10)  # Text widget to display sent data
    sent_data_text.pack()

    sent_data_scrollbar = tk.Scrollbar(window, command=sent_data_text.yview)  # Scrollbar for the text widget
    sent_data_text['yscrollcommand'] = sent_data_scrollbar.set
    sent_data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_sent_data_text():
        sent_data_text.delete("1.0", tk.END)  # Clear the text widget
        sent_data_string = "\n".join(f"{machine}: {numbers}" for machine, numbers in sent_data.items())
        sent_data_text.insert(tk.END, f"Sent Data:\n{sent_data_string}")

        # Define labels on the main screen for summary

    summary_label = tk.Label(window)
    summary_label.pack(padx=10, pady=10)

    # Define labels on the main screen for summary
    summary_label = tk.Label(window)
    summary_label.pack(padx=10, pady=10)

    def confirm_number_selection():
        global selected_machine
        global summary_label


        if len(numbers) == 0:
            messagebox.showerror("Error", "Please select at least one number.")
            return

        if selected_machine is None:
            messagebox.showerror("Error", "Please select a box.")
            return

        # Show summary screen
        summary_screen = tk.Toplevel(window)
        summary_screen.title("Summary")

        summary_label = tk.Label(summary_screen,
                                 text="Selected Numbers: {}\nSelected Box: {}".format(numbers, selected_machine))
        summary_label.pack(padx=10, pady=10)

        sent_data[selected_machine] = numbers.copy()
        update_sent_data_text()

        def confirm_selection():
            # Send data to server
            try:
                url = 'http://192.168.0.171:5550/api/receive_code/' + str(selected_machine)
                payload = {
                    'machine': selected_machine,
                    'numbers': numbers
                }
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    print(response.content)
                    messagebox.showinfo("Success", "Selection confirmed.")
                else:
                    try:
                        error_message = json.loads(response.content)['message']
                        messagebox.showerror("Error", f"Failed to send data to server: {error_message}")
                    except (ValueError, KeyError):
                        messagebox.showerror("Error",
                                             f"Failed to send data to server. Status code: {response.status_code}")
                summary_screen.destroy()
                window.deiconify()  # Show the main screen again
                machine_combobox.set('')  # Clear dropdown selection
                if check_connection():
                    print("Connection Is Already Established")
                else:
                    print("Connection not Found, Trying to Open Emulator")
                    subprocess.Popen(["python3", script_path])
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to send data to server: {str(e)}")

        confirm_button = tk.Button(summary_screen, text="Confirm", command=confirm_selection)
        confirm_button.pack(pady=10)

        def cancel_selection():
            numbers.clear()
            selected_machine = None
            # Deselect all checkboxes
            for checkbox, var in zip(checkboxes, checkbox_vars):
                var.set(False)  # Uncheck the checkbox
            machine_combobox.set('')  # Clear dropdown selection
            summary_screen.destroy()
            window.deiconify()  # Show the main screen again

        cancel_button = tk.Button(summary_screen, text="Cancel", command=cancel_selection)
        cancel_button.pack(pady=5)

        # Hide the main screen while the summary screen is open
        window.withdraw()

    def update_number_colors():
        for number, checkbox, checkbox_var in zip(range(1, len(checkboxes) + 1), checkboxes, checkbox_vars):
            duplicate_numbers = query_duplicate_numbers(number)
            if duplicate_numbers:  # if the number is a duplicate
                checkbox.configure(foreground='red')
                if number in numbers:  # if the duplicate number is in the numbers list
                    checkbox_var.set(False)  # Deselect checkbox
            else:
                checkbox.configure(foreground='green')

    def add_number(number):
        if number not in numbers:
            duplicate_numbers = query_duplicate_numbers(number)
            if duplicate_numbers:
                messagebox.showwarning("Warning", f"Duplicate numbers found: {duplicate_numbers}")
                checkbox_vars[number - 1].set(False)  # Deselect checkbox
            else:
                numbers.append(number)
        else:
            numbers.remove(number)
        update_number_colors()

    def on_checkbox_change(checkbox_var, number):
        if checkbox_var:
            add_number(number)
        else:
            remove_number(number)

    def remove_number(number):
        if number in numbers:
            numbers.remove(number)
        update_number_colors()

    def query_duplicate_numbers(number):
        try:
            url = 'http://192.168.0.171:5550/api/check_duplicates'
            payload = {
                'numbers': [number]
            }
            response = requests.post(url, json=payload)
            if response.status_code == 400:  # Server returns 400 status code when duplicates found
                data = response.json()
                duplicate_numbers = data.get('duplicate_numbers', [])  # Update this line
                return duplicate_numbers
            else:
                print(f"Failed to query duplicate numbers. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error querying duplicate numbers: {e}")
        return []

    def on_machine_selection(event):
        global selected_machine
        selected_machine = machine_combobox.get()

    number_label = tk.Label(window, text="Select Numbers:")
    number_label.pack(pady=10)

    checkboxes_frame = ttk.Frame(window)
    checkboxes_frame.pack()

    for i in range(1, 13):
        checkbox_var = tk.BooleanVar()
        checkbox_var.trace('w', lambda name, index, mode, checkbox_var=checkbox_var, i=i: on_checkbox_change(
            checkbox_var.get(), i))
        checkbox = tk.Checkbutton(checkboxes_frame, text=str(i), variable=checkbox_var)
        checkbox.grid(row=(i - 1) // 5, column=(i - 1) % 5, padx=10, pady=5)
        checkboxes.append(checkbox)  # Store checkbox reference
        checkbox_vars.append(checkbox_var)  # Store BooleanVar reference

    machine_label = tk.Label(window, text="Select Box:")
    machine_label.pack(pady=10)

    machine_combobox = ttk.Combobox(window, values=["Caixa-1", "Caixa-2", "Caixa-3", "Caixa-4"])
    machine_combobox.bind("<<ComboboxSelected>>", on_machine_selection)
    machine_combobox.pack(pady=5)

    next_button = tk.Button(window, text="Next", command=confirm_number_selection)
    next_button.pack(pady=10)

    clear_button = tk.Button(window, text="Clear", command=clear_positions)
    clear_button.pack(pady=10)

    # Periodically update checkbox colors
    def update_colors():
        update_number_colors()
        window.after(1000, update_colors)  # Call itself after 1 second

    update_colors()
    window.mainloop()

show_number_selection_screen()
