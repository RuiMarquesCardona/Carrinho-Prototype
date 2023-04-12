from flask import Flask, request, jsonify
import threading
import requests
import tkinter as tk
import time

from gpiozero import LED
from neopixel import *

app = Flask(__name__)

# Initialize LED strip
LED_COUNT = 10  # Number of LED pixels
LED_PIN = 18  # GPIO pin connected to the pixels
LED_FREQ_HZ = 800000  # LED signal frequency in hertz
LED_DMA = 10  # DMA channel to use for generating signal
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # Set to '1' for GPIOs 13, 19, 41, 45, or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Initialize buzzer
buzzer = LED(23)

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
def turn_off_led():
    global strip
    global led_timer
    strip.fill((0, 0, 0))
    strip.show()
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
    global strip
    global current_led
    global led_timer
    
    # Turn off the current LED, if any
    if current_led:
        strip.setPixelColor(current_led, Color(0, 0, 0))
        strip.show()
        
    # Set global variable to received number
    number = number
    # Print number
    print('Number received:', number)
    
    # Update GUI label
    update_gui(number)
    
    # Turn on LED if number is 1-10, turn it off for any other number
    if 1 <= number <= 10:
        led = number-1
        strip.setPixelColor(led, Color(255, 0, 0))
        strip.show()
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        current_led = led
        # Start a timer to turn off the LED after 10 seconds
        led_timer = threading.Timer(10, turn_off_led)
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
