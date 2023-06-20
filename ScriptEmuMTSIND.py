from flask import Flask, request
import requests
import time
import threading

app = Flask(__name__)

CODE_MAP = {
    '1001': 1,
    '1002': 2,
    '1003': 3,
    '1004': 4,
    '1005': 5,
    '1006': 6,
    '1007': 7,
    '1008': 8,
    '1009': 9,
    '1010': 10,
    '1011': 11,
    '1012': 12
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
        time.sleep(10)

def send_number(number):
    # do something to calculate the number
    # send the number to another server via HTTP POST
    url = 'http://192.168.0.171:5600/api/' + str(number)
    response = requests.post(url)
    if response.status_code == 200:
        print('Number sent successfully')
    else:
        print(f'Failed to send number. Status code: {response.status_code}')

@app.route('/api/<code>', methods=['POST'])
def receive_code(code):
    # get the number corresponding to the code
    number = CODE_MAP.get(code, None)
    # do something with code (e.g. save to database)
    send_number(number)
    return 'Code received and number sent'

if __name__ == '__main__':
    porta = 5500
    connection_thread = threading.Thread(target=check_connection)
    connection_thread.start()
    app.run(host='0.0.0.0', port=porta)
