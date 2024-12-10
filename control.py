import pygame

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

def travel_command(x, y):
    print(f"Travel command with x: {x}, y: {y}")

def button_a_action():
    print("Button A pressed")

def button_b_action():
    print("Button B pressed")

def button_x_action():
    print("Button X pressed")

def button_y_action():
    print("Button Y pressed")

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
