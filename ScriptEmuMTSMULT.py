from flask import Flask, request, jsonify
import requests
import time
import threading
import re
import tkinter as tk
import subprocess

app = Flask(__name__)

readCode = ''
input_buffer = ''
input_timestamp = 0

CODE_MAP = {
    'Caixa-1': '10001',
    'Caixa-2': '10002',
    'Caixa-3': '10003',
    'Caixa-4': '10004'
}

positions = {
    '10001': [],
    '10002': [],
    '10003': [],
    '10004': []
}

def check_connection():
    url = 'http://192.168.0.171:5600/api/check_connection'
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print('Connection established')
            else:
                print(f'Failed to establish connection. Status code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'Error connecting to {url}: {e}')
        time.sleep(5)

def send_numbers_to_server(payload):
    try:
        url = 'http://192.168.0.171:5600/api/control_leds'
        response = requests.post(url, json=payload)
        print(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error sending numbers to server: {e}")

def process_input():
    global readCode, input_buffer, input_timestamp

    def key_press(event):
        global input_buffer, input_timestamp, readCode
        char = event.char
        if char.isalnum():
            input_buffer += char
            input_timestamp = time.time()
            readCode = input_buffer
            text_var.set(readCode)
        elif char == '\r':
            if input_buffer:
                try:
                    code = input_buffer
                    readCode = input_buffer
                    print(f"Keyboard input: {code}")
                    # Send data to server
                    if code in CODE_MAP.values():
                        machine = list(CODE_MAP.keys())[list(CODE_MAP.values()).index(code)]
                        selected_numbers = positions[code]
                        payload = {
                            'machine': machine,
                            'numbers': selected_numbers
                        }
                        print(f"Sending data to server: {payload}")
                        send_numbers_to_server(payload)
                    else:
                        print(f"Invalid code: {code}")
                except ValueError:
                    print(f"Invalid input: {input_buffer}")
                input_buffer = ''  # Clear the input buffer
                input_timestamp = 0  # Reset the input timestamp
                readCode = ''
                text_var.set(readCode)
        else:
            print(f"Invalid input: {char}")

    root = tk.Tk()
    root.title("Keyboard Input")

    screen_width, screen_height = 50, 15  # Change these values to match your screen size
    text_var = tk.StringVar()
    label = tk.Label(root, textvariable=text_var, width=screen_width, height=screen_height)
    label.pack()

    root.bind('<Key>', key_press)
    root.mainloop()


@app.route('/api/check_connection', methods=['GET'])
def check_connection():
    return 'Connection successful'

@app.route('/api/receive_code/<machine>', methods=['POST'])
def receive_code(machine):
    # Check if the machine is valid
    if machine in CODE_MAP.keys():
        # Get the JSON payload
        payload = request.get_json()

        # Check if the payload is a valid JSON object
        if not payload or not isinstance(payload, dict):
            return jsonify(message='Invalid payload format. Expected JSON object.'), 400

        # Print the payload for debugging
        print('Received payload:', payload)

        # Get the machine and numbers from the payload
        selected_machine = payload.get('machine')
        selected_numbers = payload.get('numbers')

        if selected_machine and selected_numbers:
            # Check for duplicate numbers in positions
            duplicate_numbers = []
            for number in selected_numbers:
                for position_numbers in positions.values():
                    if number in position_numbers:
                        duplicate_numbers.append(number)
                        break

            if duplicate_numbers:
                return jsonify(message=f"Duplicate numbers found: {duplicate_numbers}"), 400

            # Add the numbers to the corresponding machine
            code = CODE_MAP[selected_machine]  # Get the code
            positions[code] = selected_numbers
            print(f"Received numbers for {selected_machine}: {selected_numbers}")
            return 'Numbers received and processed'
        else:
            return jsonify(message='Invalid payload. Missing machine or numbers.'), 400
    else:
        return jsonify(message='Invalid machine'), 400

@app.route('/api/check_duplicates', methods=['POST'])
def check_duplicates():
    # Get the JSON payload
    payload = request.get_json()

    # Check if the payload is a valid JSON object
    if not payload or not isinstance(payload, dict):
        return jsonify(message='Invalid payload format. Expected JSON object.'), 400

    # Get the numbers from the payload
    numbers = payload.get('numbers')

    if numbers:
        # Check for duplicate numbers
        duplicate_numbers = []
        for number in numbers:
            is_duplicate = False
            for position_numbers in positions.values():
                if number in position_numbers:
                    duplicate_numbers.append(number)
                    is_duplicate = True
                    break
            if not is_duplicate:
                duplicate_numbers.append(None)  # Append None if the number is not a duplicate

        # Check if any duplicates were found
        if any(duplicate_numbers):
            return jsonify(duplicate_numbers=duplicate_numbers), 400  # Return 400 status code for duplicates found
        else:
            return jsonify(duplicate_numbers=duplicate_numbers), 200  # Return 200 status code for no duplicates found

    return jsonify(message='Invalid payload. Missing numbers.'), 400

@app.route('/api/clear_positions', methods=['POST'])
def clear_positions():
    # Clear the positions dictionary
    for key in positions.keys():
        positions[key] = []

    return jsonify(message='Positions cleared'), 200

@app.route('/api/get_current_selections', methods=['GET'])
def get_current_selections():
    return jsonify(positions)


def main():
    threading.Thread(target=check_connection).start()
    threading.Thread(target=process_input).start()
    app.run(host='0.0.0.0', port=5550)


if __name__ == '__main__':
    main()
