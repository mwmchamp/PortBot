import cv2
import numpy as np

cap = cv2.VideoCapture(0)  # Access the Pi camera
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow("Camera Feed", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define HSV ranges for target colors (e.g., red, blue, green)
    red_lower = np.array([0, 120, 70])
    red_upper = np.array([10, 255, 255])
    mask_red = cv2.inRange(hsv, red_lower, red_upper)
    
    blue_lower = np.array([110, 50, 50])
    blue_upper = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv, blue_lower, blue_upper)
    
    green_lower = np.array([36, 25, 25])
    green_upper = np.array([86, 255, 255])
    mask_green = cv2.inRange(hsv, green_lower, green_upper)
    
    # Combine masks for visualization
    mask = mask_red + mask_blue + mask_green
    
    # Find contours for detected objects
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter out small contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    cv2.imshow("Detected Colors", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()