import cv2
import numpy as np
import imutils
import argparse
import time

# Define color ranges for Rubik's cube
color_ranges = {
    "Red": ([0, 100, 100], [10, 255, 255], [170, 100, 100], [180, 255, 255]),
    "Blue": ([90, 100, 100], [130, 255, 255]),
    "Green": ([40, 70, 70], [80, 255, 255]),
    "Yellow": ([20, 100, 100], [30, 255, 255]),
    "Orange": ([10, 100, 100], [20, 255, 255]),
    "White": ([0, 0, 200], [180, 30, 255])  # Adjust these values for white detection
}

def detect_color_target(frame, grid_size=3):
    height, width = frame.shape[:2]
    step_x = width // grid_size
    step_y = height // grid_size
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_colors = []

    for row in range(grid_size):
        for col in range(grid_size):
            start_x = col * step_x
            start_y = row * step_y
            end_x = start_x + step_x
            end_y = start_y + step_y
            roi = hsv[start_y:end_y, start_x:end_x]

            for color, (lower1, upper1, *rest) in color_ranges.items():
                mask = cv2.inRange(roi, np.array(lower1), np.array(upper1))
                if rest:
                    lower2, upper2 = rest
                    mask2 = cv2.inRange(roi, np.array(lower2), np.array(upper2))
                    mask = cv2.bitwise_or(mask, mask2)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)

                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                for c in cnts:
                    area = cv2.contourArea(c)
                    if area > 100:  # Minimum area to avoid noise
                        x, y, w, h = cv2.boundingRect(c)
                        if 0.8 <= float(w) / h <= 1.2:  # Ensure square-like shape
                            cv2.rectangle(frame, (start_x + x, start_y + y), (start_x + x + w, start_y + y + h), (0, 255, 0), 2)
                            cv2.putText(frame, color, (start_x + x, start_y + y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            detected_colors.append(color)
    
    return detected_colors

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def main_loop(cap):
    while True:
        frame = capture_frame(cap)
        detected_colors = detect_color_target(frame)

        if detected_colors:
            print(f"Warna terdeteksi: {', '.join(detected_colors)}")
            # You can add actions based on detected colors

        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

def main():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    time.sleep(2.0)

    main_loop(cap)

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())
    main()
