import cv2
import numpy as np
from collections import deque
import imutils
import argparse
import time

def detect_color_target(frame, start_x, start_y, end_x, end_y):
    roi = frame[start_y:end_y, start_x:end_x]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(hsv, colorLowerRed, colorUpperRed)
    mask_red2 = cv2.inRange(hsv, colorLowerRed2, colorUpperRed2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_red = cv2.erode(mask_red, None, iterations=2)
    mask_red = cv2.dilate(mask_red, None, iterations=2)

    mask_blue = cv2.inRange(hsv, colorLowerBlue, colorUpperBlue)
    mask_blue = cv2.erode(mask_blue, None, iterations=2)
    mask_blue = cv2.dilate(mask_blue, None, iterations=2)

    cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_red = imutils.grab_contours(cnts_red)

    cnts_blue = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_blue = imutils.grab_contours(cnts_blue)

    red_detected = False
    blue_detected = False

    for cnts, color in [(cnts_red, "Merah"), (cnts_blue, "Biru")]:
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)

            if len(approx) >= 4:  # Jika bentuknya memiliki lebih dari atau sama dengan 4 sudut (misalnya persegi atau segiempat)
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x + start_x, y + start_y), (x + w + start_x, y + h + start_y), (0, 255, 0), 2)
                cv2.putText(frame, color, (x + start_x, y + start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                if color == "Merah":
                    red_detected = True
                elif color == "Biru":
                    blue_detected = True

    return red_detected, blue_detected


def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame


def main_loop(cap, width, height):
    frame = None
    while True:
        frame = capture_frame(cap)
        red_detected, blue_detected = detect_color_target(frame, start_x, start_y, start_x + box_size, start_y + box_size)
        
        if red_detected and blue_detected:
            print("Kedua warna terdeteksi!")
            # Lakukan tindakan sesuai kebutuhan
            
        elif red_detected:
            print("Warna Merah terdeteksi!")
            # Lakukan tindakan sesuai kebutuhan
            
        elif blue_detected:
            print("Warna Biru terdeteksi!")
            # Lakukan tindakan sesuai kebutuhan
            
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break


# Fungsi utama
def main():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    time.sleep(2.0)

    frame = capture_frame(cap)
    height, width, _ = frame.shape

    global start_x, start_y, box_size
    box_size = 100
    start_x = int((width - box_size) / 2)
    start_y = int((height - box_size) / 2)

    main_loop(cap, width, height)

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())
    
    colorLowerRed = np.array([0, 100, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([170, 100, 100]) 
    colorUpperRed2 = np.array([180, 255, 255]) 

    colorLowerBlue = np.array([90, 100, 100])   # Membuat biru lebih terang
    colorUpperBlue = np.array([130, 255, 255])  # Membuat biru lebih terang


    main()
