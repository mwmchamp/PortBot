import pygame
from serial import Serial
import time
from osc import PORT

bottomFull = False
numBoxes = 0
# Initialize Pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()

# Check if there is a joystick connected
if pygame.joystick.get_count() < 1:
    raise Exception("No joystick connected")

# Get the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Initialize UART communication
uart = Serial(port=PORT, baudrate=115200)  # Adjust the port and baud rate as needed

def send_command_and_wait(command):
    uart.write(command)
    print(f"sent {command}")
    # Block other commands until '1' is received over UART
    while True:
        print(uart.in_waiting)
        if uart.in_waiting > 0:
            print("Fuck you")
            response = uart.read()
            print(response)
            if response == b'1':
                break
    print("Request completed")

def travel_command(x, y):
    # Define a deadzone threshold
    deadzone_threshold = 0.1
    
    # Apply deadzone logic
    if abs(x) < deadzone_threshold:
        x = 0
    if abs(y) < deadzone_threshold:
        y = 0

    if y >= 0:
        send_command_and_wait(f"FORWARD {y}".encode())
    else:
        send_command_and_wait(f"BACK {-y}".encode())

    # Map x from -1 to 1 to 90 to 150
    x_mapped = 90 + ((x + 1) / 2) * (150 - 90)
    
    # Send the STEER command with the mapped x value
    send_command_and_wait(f"STEER {x_mapped}".encode())

    print(f"Travel command with x: {x}, y: {-y}")

def button_a_action():
    print("Button A pressed")

def button_b_action():
    print("Button B pressed")

def button_x_action():
    global numBoxes, bottomFull
    print("Button X pressed")
    if numBoxes < 3:
        if bottomFull:
            send_command_and_wait(b"LIFT UP")
        send_command_and_wait(b"EXCHANGE IN")
        bottomFull = True
        numBoxes += 1

def button_y_action():
    global numBoxes, bottomFull
    print("Button Y pressed")
    if numBoxes > 0:
        if bottomFull:
            send_command_and_wait(b"EXCHANGE OUT")
            send_command_and_wait(b"BACK 100")
            time.sleep(1.5)
            send_command_and_wait(b"FORWARD 0")
            numBoxes -= 1
            bottomFull = False
            if numBoxes > 0:
                send_command_and_wait(b"LIFT DOWN")
                bottomFull = True

        
    

# Main loop to handle joystick events
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(0):  # A button
                button_a_action()
            elif joystick.get_button(1):  # B button
                button_b_action()
            elif joystick.get_button(2):  # X button
                button_x_action()
            elif joystick.get_button(3):  # Y button
                button_y_action()
        elif event.type == pygame.JOYAXISMOTION:
            # Assuming axis 0 is the x-axis and axis 1 is the y-axis of the left joystick
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            travel_command(x_axis, y_axis)

# Quit Pygame
pygame.quit()
