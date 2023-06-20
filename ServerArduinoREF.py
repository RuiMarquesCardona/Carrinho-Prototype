import flask
from flask import Flask, request, jsonify
from serial import Serial
import threading
import time

app = Flask(__name__)

# Initialize Arduino connection
arduino = Serial('COM1', 9600)  # Use appropriate serial port for your system
time.sleep(2)  # Waiting for arduino to be ready

# Define LED colors
LED_COLORS = {
    'Caixa-1': 'R',  # Red
    'Caixa-2': 'G',  # Green
    'Caixa-3': 'Y',  # Yellow
    'Caixa-4': 'B'   # Blue
}

LED_MAPPING = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
    4: [7, 8],
    5: [9, 10],
    6: [11, 12],
    7: [13, 14],
    8: [15, 16],
    9: [17, 18],
    10: [19, 20],
    11: [21, 22],
    12: [23, 24],
}

# Global variables
led_timer = None

def turn_off_all_leds():
    arduino.write(b'0\n')  # Sending '0' to turn off all LEDs on Arduino
    print("All LEDs turned off")

# Flask routes
@app.route('/api/check_connection', methods=['GET'])
def check_connection():
    return 'Connection successful'

@app.route('/api/control_leds', methods=['POST'])
def control_leds():
    payload = request.get_json()
    if not payload or not isinstance(payload, dict):
        return jsonify(message='Invalid payload format. Expected JSON object.'), 400

    machine = payload.get('machine')
    numbers = payload.get('numbers')
    if machine and numbers:
        global led_timer
        if led_timer:
            led_timer.cancel()
        turn_off_all_leds()  # Turn off all LEDs before turning new ones on

        if machine in LED_COLORS:
            color = LED_COLORS[machine]
            led_nums = [str(led) for num in numbers for led in LED_MAPPING.get(num, [])]
            led_command = ','.join(led_nums) + '-' + color + '\n'
            arduino.write(led_command.encode())  # Sending LED numbers and color to Arduino

            arduino_response = arduino.readline().decode().strip()
            print('Arduino response:', arduino_response)

            # Start turn-off timer
            led_timer = threading.Timer(10, turn_off_all_leds)
            led_timer.start()

        print(f"Received numbers for {machine}: {numbers}")
        return 'Numbers received and processed'
    else:
        return jsonify(message='Invalid payload. Missing machine or numbers.'), 400

@app.route('/api/<int:number>', methods=['POST'])
def receive_number(number):
    global led_timer

    # Print number
    print('Number received:', number)

    # Turn off the current LED and mapped LED, if any
    if led_timer:
        led_timer.cancel()
    turn_off_all_leds()  # Turn off all LEDs before turning new ones on

    # Turn on LED if number is 1-13, turn it off for any other number
    if 1 <= number <= 12:
        leds = LED_MAPPING[number]
        led_command = ','.join(str(led) for led in leds) + '-R\n'
        arduino.write(led_command.encode())  # Sending LED index and color to Arduino
        print(f"Turned on LEDs {leds} with color Red")

        led_timer = threading.Timer(10, turn_off_all_leds)
        led_timer.start()
    else:
        print("Wrong Number Received")

    # Return response to client
    return 'Number received'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5600)
