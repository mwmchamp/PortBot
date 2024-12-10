import time
import cv2
import torch

raspi = True
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
    raspi = False
    
from ultralytics import YOLO
from osc import CAM

# Load the YOLO model
model = YOLO("bestAll.pt")

# Define the target class
target_classes = ["orange", "white", "black"]

if raspi:
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    input_pin = 17  # Example GPIO pin for input
    output_pin = 27  # Example GPIO pin for output
    pwm_pin = 22  # Example GPIO pin for PWM output
    color_select_pin = 23  # Example GPIO pin for color selection

    GPIO.setup(input_pin, GPIO.IN)
    GPIO.setup(output_pin, GPIO.OUT)
    GPIO.setup(pwm_pin, GPIO.OUT)
    # Setup the color select pin
    GPIO.setup(color_select_pin, GPIO.IN)

    # Function to get the selected color based on GPIO input
    def get_selected_color():
        if GPIO.input(color_select_pin) == GPIO.HIGH:
            return "orange"
        else:
            return "black"

    # Initialize PWM
    pwm = GPIO.PWM(pwm_pin, 333)  # 1kHz frequency
    pwm.start(0)

    # Open the webcam
    cap = cv2.VideoCapture("/dev/video0")
else:
    print("GPIO setup would occur here if running on Raspberry Pi.")
    input_pin = 17
    output_pin = 27
    pwm_pin = 22
    color_select_pin = 23

    def get_selected_color():
        print("Simulating GPIO input for color selection.")
        return "orange"

    class MockPWM:
        def __init__(self, pin, frequency):
            self.pin = pin
            self.frequency = frequency

        def start(self, duty_cycle):
            print(f"Starting PWM on pin {self.pin} with frequency {self.frequency}Hz and duty cycle {duty_cycle}%.")

        def ChangeDutyCycle(self, duty_cycle):
            print(f"Changing PWM duty cycle on pin {self.pin} to {duty_cycle}%.")

        def stop(self):
            print(f"Stopping PWM on pin {self.pin}.")

    pwm = MockPWM(pwm_pin, 333)

    # Open the webcam
    cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("Error: Cannot access the camera.")
    exit()

while True:
    # Wait for the input pin to go high
    if raspi:
        while GPIO.input(input_pin) == GPIO.LOW:
            time.sleep(0.1)
    else:
        print("Simulating waiting for input pin to go high.")
        time.sleep(5)

    sel_color = get_selected_color()

    # Set the output pin high
    if raspi:
        GPIO.output(output_pin, GPIO.HIGH)
    else:
        print("Simulating setting output pin high.")

    # Initialize variables to track disappearance
    last_seen_time = time.time()
    disappeared = False

    while not disappeared:
        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame.")
            break

        # Get results from the model
        results = model(frame)

        # Check if the selected target class is detected
        target_detected = False
        x_offset = 0
        for result in results:
            print("examining")
            for detection in result.boxes:
                print("examining box")
                class_name = detection.cls
                print(class_name)
                if class_name.item() == 1:
                    print(f"there is a {class_name}")
                    target_detected = True
                    # Calculate x offset using xywh format
                    if len(detection.xywh) >= 3:
                        x_center = detection.xywh[0] + (detection.xywh[2] / 2)
                        x_offset = x_center - (frame.shape[1] / 2)
                    else:
                        print("Error: xywh format is incomplete.")
                    break  # Exit loop once the selected color is found
            if target_detected:
                break  # Exit outer loop if the selected color is found

        # Output PWM signal based on x offset
        pwm_duty_cycle = (x_offset / (frame.shape[1] / 2)) * 24 + 47  # Map to 35-59%
        pwm.ChangeDutyCycle(max(0, min(100, pwm_duty_cycle)))

        # Update last seen time if target is detected
        if target_detected:
            print(last_seen_time, "is the last time")
            last_seen_time = time.time()
            disappeared = False
        else:
            # Check if the target has disappeared for more than 0.5 seconds
            delta = time.time() - last_seen_time
            print(delta, "is the time")
            if delta > 1 and not disappeared:
                print("Target has disappeared from the frame.")
                disappeared = True

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Set the output pin low
    if raspi:
        GPIO.output(output_pin, GPIO.LOW)
    else:
        print("Simulating setting output pin low.")

# Release resources
cap.release()
pwm.stop()
if raspi:
    GPIO.cleanup()
cv2.destroyAllWindows()
