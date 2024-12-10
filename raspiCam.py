import cv2

def display_raspi_camera():
    # Open the Raspberry Pi camera
    cap = cv2.VideoCapture(0)  # 0 is usually the default camera

    if not cap.isOpened():
        print("Error: Cannot access the Raspberry Pi camera.")
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
