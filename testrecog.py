from ultralytics import YOLO
import cv2
import os

# Load a model
# model = YOLO("yolo11n.pt")  # load an official model
model = YOLO("bestAll.pt")  # load a custom model

use_webcam = True

# Directory containing images
image_dir = "/Users/mwmchamp/Library/CloudStorage/OneDrive-PrincetonUniversity/Semester5/CarLab/PortBot/test/images"

def process_image(input_source, model, is_webcam=False):
    # Predict with the model
    if is_webcam:
        results = model(input_source)  # predict on a frame
    else:
        results = model(input_source)  # predict on an image
    print(results)
    return results

# Check if the input source is a webcam or directory
  # Set to True to use webcam

if use_webcam:
    # Open the webcam
    cap = cv2.VideoCapture("/dev/video0")
    if not cap.isOpened():
        print("Error: Cannot access the camera.")
        exit()

    while True:
        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame.")
            break

        # Get results from the function
        results = process_image(frame, model, is_webcam=True)

        # Assuming 'results' is a list of detections, iterate over them
        for result in results:
            # Get the image with the bounding boxes and labels drawn
            annotated_frame = result.plot()

            # Display the image using OpenCV
            cv2.imshow("Detection Results", annotated_frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
else:
    # Iterate through the images in the directory
    for image_name in os.listdir(image_dir):
        if image_name.endswith(('.jpg', '.jpeg', '.png')):  # Check for image files
            image_path = os.path.join(image_dir, image_name)
            
            # Get results from the function
            results = process_image(image_path, model)

            # Assuming 'results' is a list of detections, iterate over them
            for result in results:
                # Get the image with the bounding boxes and labels drawn
                annotated_frame = result.plot()

                # Display the image using OpenCV
                cv2.imshow("Detection Results", annotated_frame)

                # Wait for a key press to close the window
                cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()

