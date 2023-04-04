from flask import Flask, request, jsonify
from gpiozero import LED, Button
import threading
import requests
import tkinter as tk
import time

app = Flask(__name__)

# Initialize LEDs and buzzer
pin_leds = [4, 17, 27, 22, 5, 6, 13, 19, 26, 21]
leds = [LED(pin) for pin in pin_leds]
button = Button(2)
buzzer = LED(18)
buzzer.on()
time.sleep(0.1)
buzzer.off()

# Define GUI
def create_gui():
    global label
    root = tk.Tk()
    root.geometry('500x500')
    label = tk.Label(root, text="Pronto para ler!", font=('calibri', 14))
    label.pack(expand=True, fill='both')
    root.mainloop()

def update_gui(number):
    global label
    number = number
    if 1 <= number <= 10:
        label.config(text="Objeto Lido! Número do Objeto: {}".format(number))
    else:
        label.config(text="Pronto para ler!")

def reset_gui():
    global label
    label.config(text="Pronto para ler!")

# Define function to turn off the LED after 10 seconds
def turn_off_led(led):
    time.sleep(10)
    led.off()
    reset_gui()

# Start GUI thread
gui_thread = threading.Thread(target=create_gui)
gui_thread.start()

# Flask routes
@app.route('/api/check_connection', methods=['GET'])
def check_connection():
    return "", 200

@app.route('/api/<int:number>', methods=['POST'])
def receive_number(number):
    global leds
    global current_led
    global led_timer
    
    # Turn off the current LED, if any
    if current_led:
        current_led.off()
        
    # Set global variable to received number
    number = number
    # Print number
    print('Number received:', number)
    
    # Update GUI label
    update_gui(number)
    
    # Turn on LED if number is 1-10, turn it off for any other number
    if 1 <= number <= 10:
        led = leds[number-1]
        led.on()
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        current_led = led
        # Start a timer to turn off the LED after 10 seconds
        led_timer = threading.Timer(0, turn_off_led, args=[led])
        led_timer.start()
    else:
        print("Wrong Number Received")
    
    # Return response to client
    return 'Number received'

if __name__ == '__main__':
    # Run Flask app
    porta=5555
    current_led = None
    led_timer = None
    app.run(host='0.0.0.0', port=porta)
