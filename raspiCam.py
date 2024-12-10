import cv2

def display_raspi_camera():
    # Open the Raspberry Pi camera using GStreamer pipeline
    gst_pipeline = "v4l2src ! videoconvert ! appsink"
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("Error: Cannot access the Raspberry Pi camera. GStreamer pipeline failed to start.")
        return

    try:
        while True:
            # Capture a frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Cannot read frame from the camera.")
                break

            # Display the frame
            cv2.imshow("Raspberry Pi Camera", frame)

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Release the camera and close all OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    display_raspi_camera()
