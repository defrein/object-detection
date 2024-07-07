import cv2
import os
import time
import threading
from datetime import datetime

# Directory to save the images
save_dir = "webcam_images"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Global variable to store the latest frame
latest_frame = None
frame_lock = threading.Lock()

def capture_frame(cap):
    global latest_frame
    while True:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                latest_frame = frame.copy()
        time.sleep(0.03)  # Approx 30 fps capture

def save_frame(frame, save_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(save_dir, f"image_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Saved: {filename}")

def main_loop(interval=3):
    global latest_frame
    last_save_time = time.time()
    
    while True:
        with frame_lock:
            if latest_frame is not None:
                frame = latest_frame.copy()
                cv2.imshow('Webcam Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Save frame every 'interval' seconds
        if time.time() - last_save_time >= interval:
            with frame_lock:
                if latest_frame is not None:
                    save_frame(latest_frame, save_dir)
            last_save_time = time.time()

def main():
    global latest_frame
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    time.sleep(2.0)  # Give the camera some time to warm up

    # Start the capture thread
    capture_thread = threading.Thread(target=capture_frame, args=(cap,), daemon=True)
    capture_thread.start()

    try:
        main_loop()
    except KeyboardInterrupt:
        print("Exiting...")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
