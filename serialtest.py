import serial
import time
import threading

# create an empty list
buffer = []
COM_PORT = "COM7"
# open a serial port
# use COM_ (or put your own port in here)
# baudrate 115200 is the default setting for the XBee
# timeout = 1 ensure the serial port won't read forever (we don't use flow control)
s=serial.Serial(COM_PORT,baudrate=115200,timeout=1)


def listen_to_psoc():
    """
    Continuously listen for responses from the PSoC and display them.
    Runs on a separate thread.
    """
    while True:
        try:
            response = s.readline().decode('utf-8').strip()  # Read a line from UART
            if response:
                print(f"\nReceived from PSoC: {response}")
        except serial.SerialException as e:
            print(f"Error reading from UART: {e}")
            break


# Start a background thread to listen to the PSoC
listener_thread = threading.Thread(target=listen_to_psoc, daemon=True)
listener_thread.start()

# Main loop to take user input and send it to the PSoC
try:
    print("Type your messages below. Type 'exit' to quit.")
    while True:
        user_input = input("Send to PSoC: ")  # Take input from the terminal
        if user_input.lower() == 'exit':
            break  # Exit the loop and terminate
        s.write((user_input + '\n').encode('utf-8'))  # Send input over UART
        print(f"Sent: {user_input}")
except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    s.close()  # Ensure the serial port is closed
    print("Serial port closed.")


