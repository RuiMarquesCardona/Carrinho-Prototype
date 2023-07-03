import flask
from flask import Flask, request, jsonify
import serial
import threading
import time

app = Flask(__name__)

# Configure the serial port
ser = serial.Serial('COM4', 9600)  # Replace 'COMX' with the correct port for your system
ser.timeout = 2

# Wait for Bluetooth connection
connected = False
while not connected:
    ser.write(b'hello')  # Send a message to Arduino to check connection
    response = ser.readline().strip().decode()  # Read the response from Arduino
    if response == 'connected':
        connected = True
    else:
        print("Waiting for Bluetooth connection...")
        time.sleep(1)

print("Bluetooth connected!")

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
    ser.write(b'0\n')  # Sending '0' to turn off all LEDs on Arduino
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
            ser.write(led_command.encode())  # Sending LED numbers and color to Arduino

            arduino_response = ser.readline().decode().strip()
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
        ser.write(led_command.encode())  # Sending LED index and color to Arduino
        print(f"Turned on LEDs {leds} with color Red")

        led_timer = threading.Timer(10, turn_off_all_leds)
        led_timer.start()
    else:
        print("Wrong Number Received")

    # Return response to client
    return 'Number received'

def send_data_over_bluetooth(data):
    ser.write(data.encode())  # Send data to Arduino

    received_data = ser.readline().decode().strip()  # Read data from Arduino
    print("Received data:", received_data)

@app.route('/api/send_data', methods=['POST'])
def send_data():
    payload = request.get_json()
    if not payload or not isinstance(payload, dict):
        return jsonify(message='Invalid payload format. Expected JSON object.'), 400

    data = payload.get('data')
    if data:
        threading.Thread(target=send_data_over_bluetooth, args=(data,)).start()
        return 'Data sent over Bluetooth'
    else:
        return jsonify(message='Invalid payload. Missing data.'), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5600)
