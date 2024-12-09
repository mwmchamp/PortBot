import cv2
import numpy as np
from cvzone.ColorModule import ColorFinder

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Initialize ColorFinder
color_finder = ColorFinder(True)
red_hsv_values = {'hmin': 0, 'smin': 100, 'vmin': 100, 'hmax': 10, 'smax': 255, 'vmax': 255}
green_hsv_values = {'hmin': 40, 'smin': 100, 'vmin': 100, 'hmax': 80, 'smax': 255, 'vmax': 255}

# Define focal length and real box dimensions (for distance calculation)
KNOWN_WIDTH = 5.0  # cm
FOCAL_LENGTH = 600  # Focal length in pixels (calibrate for accuracy)

def calculate_distance(pixel_width):
    return (KNOWN_WIDTH * FOCAL_LENGTH) / pixel_width

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame.")
        break

    frame_h, frame_w, _ = frame.shape
    center_x = frame_w // 2

    # Process for red boxes
    red_mask, red_img = color_finder.update(frame, red_hsv_values)
    red_mask = cv2.cvtColor(red_mask, cv2.COLOR_BGR2GRAY)  # Ensure mask is single-channel
    contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Process for green boxes
    green_mask, green_img = color_finder.update(frame, green_hsv_values)
    green_mask = cv2.cvtColor(green_mask, cv2.COLOR_BGR2GRAY)  # Ensure mask is single-channel
    contours_green, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    data_to_send = []

    # Function to process each color
    def process_contours(contours, color_name):
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:  # Filter noise
                x, y, w, h = cv2.boundingRect(cnt)
                distance = calculate_distance(w)
                box_center_x = x + w // 2
                left_right = "Left" if box_center_x < center_x else "Right"
                data_to_send.append(f"{color_name}:{distance:.2f}cm,{left_right}")

                # Draw bounding box and center point
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0) if color_name == 'Green' else (0, 0, 255), 2)
                cv2.circle(frame, (box_center_x, y + h // 2), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"{distance:.2f}cm, {left_right}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Process red and green contours
    process_contours(contours_red, "Red")
    process_contours(contours_green, "Green")

    # Print data to terminal
    if data_to_send:
        serial_data = "|".join(data_to_send) + "\n"
        print(serial_data.strip())

    # Display the result
    cv2.imshow("Tracking", frame)

    # Quit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
