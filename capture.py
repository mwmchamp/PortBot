import cv2
import os
import time

# Set up the output directory
output_dir = "captured_images"
os.makedirs(output_dir, exist_ok=True)

# Open the webcam
cap = cv2.VideoCapture(0)  # Use the appropriate index for your camera
if not cap.isOpened():
    print("Error: Cannot access the camera.")
    exit()

print("Press 'Space' to capture a picture. Press 'q' to quit.")

image_count = 0

while True:
    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read frame.")
        break

    # Display the frame
    cv2.imshow("Webcam - Move the object to capture different angles", frame)

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF

    # Capture an image when 'Space' is pressed
    if key == ord(' '):
        image_path = os.path.join(output_dir, f"image_{image_count:04d}.jpg")
        cv2.imwrite(image_path, frame)
        print(f"Saved: {image_path}")
        image_count += 1

    # Exit on 'q' key
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
