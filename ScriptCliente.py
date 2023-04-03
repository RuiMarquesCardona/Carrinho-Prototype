import cv2
import requests
import time
import numpy as np

input_buffer = ''
input_timestamp = 0

# Create a window to display the keyboard input
cv2.namedWindow('Keyboard Input', cv2.WINDOW_NORMAL)

while True:
    # Convert the input buffer to a NumPy array for display
    img = np.zeros((100, 400, 3), dtype=np.uint8)
    cv2.putText(img, input_buffer, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Show the current input buffer in the GUI window
    cv2.imshow('Keyboard Input', img)

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
            print(f"Keyboard input: {number}")
            # Send data to server
            url = 'http://192.168.0.171:5555/api/' + str(number)
            response = requests.post(url)
            print(response.content)
        except ValueError:
            print(f"Invalid input: {input_buffer}")
        input_buffer = ''  # Clear the input buffer
        input_timestamp = 0  # Reset the input timestamp

# Destroy the window before exiting the program
cv2.destroyAllWindows()
