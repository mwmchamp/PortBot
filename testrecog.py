import cv2
from ultralytics import YOLO

# Load the trained YOLOv8 model (best.pt)
model = YOLO('best.pt')  # Replace with the path to your model

# Open the webcam (you can change the index if using multiple cameras)
cap = cv2.VideoCapture(0)  # Use 0 for the default webcam

# Set the desired frame width and height for processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        break  # Exit if no frame is read
    
    # Run inference on the current frame
    results = model(frame)

    # Iterate over the results
    for result in results:
        # Extract boxes from the result
        boxes = result.boxes  # Use the correct attribute
        if boxes is not None:
            for box in boxes:
                x1, y1, w, h, conf, cls = map(int, box.xywh)  # Assuming box has an xywh method or property
                # Draw bounding boxes
                cv2.rectangle(frame, (x1, y1), (x1+w, y1+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Class {cls} Conf {conf:.2f}", 
                            (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Show the resulting frame with detections
    cv2.imshow('YOLOv8 Object Detection', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
