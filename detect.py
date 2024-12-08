import cv2
import cvzone
from cvzone.ColorModule import ColorFinder
import serial
import time

# Initialize serial communication
serial_port = '/dev/ttyUSB0'  # Replace with your serial port
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Initialize ColorFinder
color_finder = ColorFinder(True)  # Turn on debug mode for initial calibration

# Define HSV color range (adjust these values)
hsv_values = {'hmin': 20, 'smin': 100, 'vmin': 100, 'hmax': 30, 'smax': 255, 'vmax': 255}

# Open video capture (0 for webcam, change to video path or PiCam index if needed)
cap = cv2.VideoCapture(0)

# Give some time for the serial to initialize
time.sleep(2)

try:
    while True:
        success, frame = cap.read()
        if not success:
            print("Camera not accessible")
            break

        # Process the frame to find the colored box
        img_color, mask = color_finder.update(frame, hsv_values)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Get bounding box and center of the contour
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
            area = cv2.contourArea(contour)

            # Filter based on area
            if area > 500:  # Adjust area threshold as needed
                # Draw rectangle and center point
                cvzone.putTextRect(frame, f"Pos: ({cx}, {cy})", (x, y - 10), scale=1, thickness=2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Send position over serial
                position_data = f"{cx},{cy}\n"
                ser.write(position_data.encode())
                print(f"Sent: {position_data.strip()}")

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
