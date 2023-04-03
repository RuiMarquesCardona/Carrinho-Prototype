from flask import Flask, request
import requests

app = Flask(__name__)

CODE_MAP = {
    'CODE10'
    '': 1,
    'CODE2': 2,
    'CODE3': 3,
    'CODE4': 4,
    'CODE5': 5,
    'CODE6': 6,
    'CODE7': 7,
    'CODE8': 8,
    'CODE9': 9,
    'CODE10': 10
}

@app.route('/api/<code>', methods=['POST'])
def receive_code(code):
    # get the number corresponding to the code
    number = CODE_MAP.get(code, None)
    # do something with code (e.g. save to database)
    send_number(number)
    return 'Code received and number sent'

def send_number(number):
    # do something to calculate the number
    # send the number to another server via HTTP POST
    url = 'http://192.168.0.150:5555/api/' + str(number)
    response = requests.post(url)
    if response.status_code == 200:
        print('Number sent successfully')
    else:
        print('Failed to send number')

if __name__ == '__main__':
    porta=5555
    app.run(host='192.168.0.171', port=porta)
