import cv2
import cvzone
import serial
import numpy as np

UART = False

# Initialize serial communication
if UART:
    serial_port = '/dev/serial0'  # Default Raspberry Pi UART
    baud_rate = 9600
    ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Open the webcam
cap = cv2.VideoCapture(0)

# Define HSV ranges for target colors (e.g., red, blue, green)
color_ranges = {
    'red': ([0, 120, 70], [10, 255, 255]),
    'green': ([36, 25, 25], [86, 255, 255]),
    'blue': ([110, 50, 50], [130, 255, 255])
}

try:
    while True:
        # Read a frame from the webcam
        success, frame = cap.read()
        if not success:
            print("Failed to capture image from webcam")
            break

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Initialize variables to store the largest contour and its color
        largest_contour = None
        largest_area = 0
        target_color = None

        # Iterate over each color range
        for color, (lower, upper) in color_ranges.items():
            # Create a mask for the current color
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # Find contours for the current color
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500 and area > largest_area:  # Filter out small contours
                    largest_area = area
                    largest_contour = contour
                    target_color = color

        if largest_contour is not None:
            # Get bounding box and center of the largest contour
            x, y, w, h = cv2.boundingRect(largest_contour)
            cx, cy = x + w // 2, y + h // 2

            # Draw rectangle and center point
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cvzone.putTextRect(frame, f"Color: {target_color}", (x, y - 10), scale=1, thickness=2)

            # Calculate steering position and speed target
            frame_center = frame.shape[1] // 2
            steering_position = (cx - frame_center) / frame_center  # Normalize to range [-1, 1]
            speed_target = 1.0 if target_color == 'red' else 0.5 if target_color == 'green' else 0.2

            # Send steering position and speed target over serial or print to terminal
            data = f"{steering_position:.2f},{speed_target:.2f}\n"
            if UART:
                ser.write(data.encode())
            else:
                print(f"Sent: {data.strip()}")

        # Show the frame
        cv2.imshow("Frame", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted")

finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()
