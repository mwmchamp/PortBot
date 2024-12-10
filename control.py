import pygame
from serial import Serial
import time
from osc import PORT

bottomFull = False
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

def send_command(command):
    uart.write(command.encode()+b'\n')
    print(f"Sent: {command}")

def send_command_and_wait(command):
    uart.write(command.encode()+b'\n')
    print(f"Sent: {command}")

    start_time = time.time()
    while True:
        if uart.in_waiting > 0:
            response = uart.read()
            print(f"{response.decode()}", end="")
            if response in (b'1', b'0'):
                break
        if time.time() - start_time > 3:
            print("Timeout: No response received within 3 seconds")
            return 1
    print("")
    if response == b'1':
        print(command, "successful\n")
        return 0
    else:
        print(command, "failed\n")
        return 1

def travel_command(x, y):
    # Define dead zone threshold
    dead_zone = 0.1

    # Apply dead zone to y axis
    if abs(y) < dead_zone:
        y = 0
    else:
        # Normalize y value outside dead zone
        y = (abs(y) - dead_zone) / (1 - dead_zone) * (5 if y > 0 else -5)

    if y >= 0:
        send_command(f"BACK {y}")
    else:
        send_command(f"FORWARD {-y}")

    # Apply dead zone to x axis
    if abs(x) < dead_zone:
        x = 0
    else:
        # Normalize x value outside dead zone
        x = (abs(x) - dead_zone) / (1 - dead_zone) * (1 if x > 0 else -1)

    # Map x from -1 to 1 to 90 to 150
    x_mapped = int(90 + ((x + 1) / 2) * (150 - 90))
    
    # Send the STEER command with the mapped x value
    send_command(f"STEER {x_mapped}")

    print(f"Travel command with x: {x}, y: {-y}")

def button_a_action():
    print("Button A pressed")
    send_command_and_wait("TRACK ORANGE")

def button_b_action():
    print("Button B pressed")
    send_command_and_wait("TRACK BLACK")

def button_x_action():
    global bottomFull
    print("Button X pressed")
    send_command_and_wait("FORWARD 1")
    send_command_and_wait("EXCHANGE IN")
    send_command_and_wait("BACK 0")
    send_command_and_wait("LIFT UP")

    bottomFull = True

def button_y_action():
    global bottomFull
    print("Button Y pressed")
    if bottomFull:
        send_command_and_wait("EXCHANGE OUT")
        bottomFull = False
        send_command_and_wait("LIFT DOWN")
        bottomFull = True

        
    

# Main loop to handle joystick events
running = True
last_travel_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:  # Check if 'q' key is pressed
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

            # Add delay between travel commands
            current_time = time.time()
            if current_time - last_travel_time >= 0.2:  # 100ms delay between commands
                travel_command(x_axis, y_axis)
                last_travel_time = current_time

# Quit Pygame
pygame.quit()
