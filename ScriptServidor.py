from flask import Flask, request, jsonify
import threading
import requests
import tkinter as tk
import time

from gpiozero import LED
from rpi_ws281x import *

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
for i in range(10):
            strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
# Initialize buzzer
buzzer = LED(4)

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

lock = threading.Lock()
def turn_off_led(current_led):
    with lock:
        if current_led is not None:
            strip.setPixelColor(current_led, Color(0, 0, 0))
            strip.show()
            reset_gui()
            current_led = None

# Start GUI thread
gui_thread = threading.Thread(target=create_gui)
gui_thread.start()
buzzer.on()
time.sleep(0.1)
buzzer.off()

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
        for i in range(10):
            strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
        if led_timer:
            led_timer.cancel()
        current_led = None
    
    # Set global variable to received number
    number = number
    # Print number
    print('Number received:', number)
    
    # Update GUI label
    update_gui(number)
    
    # Turn on LED if number is 1-10, turn it off for any other number
    if 1 <= number <= 10:
    
        led = number - 1
        strip.setPixelColor(led, Color(255, 0, 0))
        strip.show()
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        if current_led is not None and current_led != led:
            strip.setPixelColor(current_led, Color(0, 0, 0))
            strip.show()
            if led_timer is not None:
                led_timer.cancel()
            current_led = None
        current_led = led
        if led_timer is not None:
            led_timer.cancel()
        led_timer = threading.Timer(10, turn_off_led, args=[current_led])
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
