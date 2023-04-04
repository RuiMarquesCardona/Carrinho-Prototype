import cv2
import numpy as np
import requests
import time
import subprocess

# Get screen dimensions
screen_width, screen_height = 640, 480  # Change these values to match your screen size

# Create black image to display text
text_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

input_buffer = ''
readCode = ''
input_timestamp = 0

script_path = "C:\Scripts\ScriptEmuMTS.py"
subprocess.Popen(["python", script_path])

while True:
    # Display text on image
    cv2.putText(text_image, readCode, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Show image
    cv2.imshow('Keyboard Input', text_image)

    # Wait for key press
    key = cv2.waitKey(1)
    if key == ord('q'):  # Exit loop if 'q' key is pressed
        break
    elif key != -1:  # Send keyboard input if any key is pressed
        # Get the character corresponding to the key pressed
        char = chr(key).strip()  # Remove any leading or trailing white spaces
        if char.isalnum():  # Check if the input is a digit
            input_buffer += char  # Add the digit to the input buffer
            input_timestamp = time.time()  # Update the input timestamp
        elif char == '\n':  # Check if the input is "Enter"
            if input_buffer:  # Check if the input buffer is not empty
                try:
                    number = input_buffer
                    readCode = input_buffer
                    print(f"Keyboard input: {number}")
                    # Send data to server
                    url = 'http://192.168.0.171:5555/api/' + str(number)
                    response = requests.post(url)
                    print(response.content)
                except ValueError:
                    print(f"Invalid input: {input_buffer}")
                input_buffer = ''  # Clear the input buffer
                input_timestamp = 0  # Reset the input timestamp
        else:
            print(f"Invalid input: {char}")

    # Check if the input buffer has been idle for more than 1 second
    if input_buffer and time.time() - input_timestamp > 0.1:
        try:
            number = input_buffer
            readCode = input_buffer
            print(f"Keyboard input: {number}")
            # Send data to server
            url = 'http://192.168.0.171:5555/api/' + str(number)
            response = requests.post(url)
            print(response.content)
        except ValueError:
            print(f"Invalid input: {input_buffer}")
        input_buffer = ''  # Clear the input buffer
        input_timestamp = 0  # Reset the input timestamp

    # Clear text from image if input buffer is empty
    if not input_buffer:
        text_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

# Release resources
cv2.destroyAllWindows()
