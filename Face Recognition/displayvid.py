import cv2

def display_video():
    # Initialize video capture with /dev/video0
    try:
        cap = cv2.VideoCapture('/dev/video0')
        print("Video capture initialized successfully.")
    except Exception as e:
        print(f"An error occurred while initializing video capture: {e}")
        return

    # Set the width and height of the video capture
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Continuously capture frames from the camera
    while True:
        # Read a frame from the video capture
        try:
            ret, frame = cap.read()
            print("read")
            if ret:
                print("Frame read successfully.")
        except Exception as e:
            print(f"An error occurred while reading a frame: {e}")
            ret, frame = False, None

        # If a frame is successfully captured
        # Display the frame in a window named 'Video'
        try:
            cv2.imshow('Video', frame)
        except Exception as e:
            print(f"An error occurred while displaying the frame: {e}")

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        print("Failed to capture video")
        break

    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    display_video()
