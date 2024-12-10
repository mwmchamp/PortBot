from osc import PORT

from serial import Serial

import time

# Initialize UART communication
uart = Serial(port=PORT, baudrate=115200)  # Adjust the port and baud rate as needed

commands = ["EXCHANGE IN", "EXCHANGE OUT", "LIFT UP", "LIFT DOWN", "STEER 100", "STEER 140", "EXCHANGE OUT", "EXCHANGE OUT", "LIFT UP"]

def send_and_wait(command):
    uart.write(command.encode()+b'\n')
    print(f"Sent: {command}")

# uart.write(b"LIFT DOWN\n")
# print("sent LIFT DOWN")

# Read and print any information received on UART
    while True:
        if uart.in_waiting > 0:
            response = uart.read()
            print(f"{response.decode()}", end="")
            if response in (b'1', b'0'):
                break
    print("")
    if response == b'1':
        print(command, "successful\n")
    else:
        print(command, "failed\n")


# Send "FORWARD 7" command
for c in commands:
    send_and_wait(c)

    time.sleep(2)

