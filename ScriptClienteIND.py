import tkinter as tk
import requests
import time
import subprocess
from threading import Thread

# Get screen dimensions
screen_width, screen_height = 50, 15  # Change these values to match your screen size

input_buffer = ''
readCode = ''
input_timestamp = 0

script_path = "C:/LEDProjekt/IndividualLEDs/ScriptEmuMTSIND.py"
subprocess.Popen(["python3", script_path])

def handle_keypress(event):
    global input_buffer, input_timestamp, readCode
    # Get the character from the keypress event
    char = event.char
    if char.isalnum():  # Check if the input is a digit
        input_buffer += char  # Add the digit to the input buffer
        input_timestamp = time.time()  # Update the input timestamp
        readCode = input_buffer
        text_var.set(readCode)
    elif char == '\r':  # Check if the input is "Enter"
        if input_buffer:  # Check if the input buffer is not empty
            try:
                number = input_buffer
                readCode = input_buffer
                print(f"Números Únicos: {number}")
                # Send data to server
                url = 'http://192.168.0.171:5500/api/' + str(number)
                response = requests.post(url)
                print(response.content)
            except ValueError:
                print(f"Invalid input: {input_buffer}")
            input_buffer = ''  # Clear the input buffer
            input_timestamp = 0  # Reset the input timestamp
            readCode = ''
            text_var.set(readCode)
    else:
        print(f"Invalid input: {char}")

root = tk.Tk()

# Set the title of the window
root.title("Números Únicos")

text_var = tk.StringVar()
label = tk.Label(root, textvariable=text_var, width=screen_width, height=screen_height)
label.pack()

root.bind('<Key>', handle_keypress)

root.mainloop()
