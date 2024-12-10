from osc import PORT

from serial import Serial

# Initialize UART communication
uart = Serial(port=PORT, baudrate=115200)  # Adjust the port and baud rate as needed

# Send "FORWARD 7" command
uart.write(b"LIFT UP\n")
print("sent LIFT UP")

uart.write(b"LIFT DOWN\n")
print("sent LIFT UP")

# Read and print any information received on UART
while True:
    if uart.in_waiting > 0:
        response = uart.read()
        print(f"Received: {response}")
        
