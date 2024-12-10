from pickle import TRUE
import time
from ultralytics import YOLO
import cv2
from osc import CAM

# Load the YOLO model
model = YOLO("bestAll.pt")

# Define the target class
target_classes = ["orange", "white", "black"]

# Open the webcam
cap = cv2.VideoCapture(CAM)
if not cap.isOpened():
    print("Error: Cannot access the camera.")
    exit()

# Initialize variables to track disappearance
last_seen_time = time.time()
disappeared = False

while True:
    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read frame.")
        break

    # Get results from the model
    results = model(frame)

    # Check if any target class is detected
    target_detected = False
    for result in results:
        for detection in result.boxes:
            class_name = detection.cls
            print(f"there is a {class_name}")
            target_detected = TRUE

    # Update last seen time if target is detected
    if target_detected:
        print(last_seen_time, "is the last time")
        last_seen_time = time.time()
        disappeared = False
    else:
        # Check if the target has disappeared for more than 0.5 seconds
        delta = time.time() - last_seen_time
        print(delta, "is the time")
        if delta > 0.4 and False == disappeared:
            print("Target has disappeared from the frame.")
            disappeared = True

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q') or disappeared:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
