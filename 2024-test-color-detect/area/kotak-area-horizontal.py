import cv2
import numpy as np
from collections import deque
import imutils
import argparse
import time

def on_trackbar_move_horizontal(pos):
    global start_x
    start_x = pos

def on_trackbar_move_vertical(pos):
    global start_y
    start_y = pos

def on_trackbar_resize(size):
    global box_size
    box_size = size

def reset_position(width, height):
    global start_x, start_y
    start_x = int((width - box_size) / 2)
    start_y = int((height - box_size) / 2)
    cv2.setTrackbarPos('Start X', 'Trackbars', start_x)
    cv2.setTrackbarPos('Start Y', 'Trackbars', start_y)

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

    # Temukan kontur dalam mask_red
    cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_red = imutils.grab_contours(cnts_red)

    # Temukan kontur dalam mask_blue
    cnts_blue = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_blue = imutils.grab_contours(cnts_blue)

    # Inisialisasi flag untuk mendeteksi setidaknya satu warna
    color_detected = False

    for cnts, color in [(cnts_red, "Merah"), (cnts_blue, "Biru")]:
        max_area = 0
        max_contour = None

        for c in cnts:
            # Dapatkan area kontur
            area = cv2.contourArea(c)

            # Pilih kontur dengan area terbesar
            if area > max_area:
                max_area = area
                max_contour = c

        if max_contour is not None:
            # Dapatkan lingkaran minimum yang melingkupi kontur
            ((x, y), radius) = cv2.minEnclosingCircle(max_contour)
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            else:
                center = (0, 0)

            # Jika radius lebih besar dari 10, gambar lingkaran dan centernya
            if radius > 10:
                cv2.circle(frame, (int(x) + start_x, int(y) + start_y), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, (center[0] + start_x, center[1] + start_y), 5, (0, 0, 255), -1)

                rel_center_x = center[0] + start_x
                rel_center_y = center[1] + start_y

                # Tambahkan teks label pada posisi yang sesuai
                label_x = rel_center_x - len(color) * 5  # Hitung posisi x untuk label
                label_y = rel_center_y + 20  # Letakkan label di bawah lingkaran
                cv2.putText(frame, color, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Cek apakah posisi relatif target ada di dalam kotak
                if start_x < rel_center_x < end_x and start_y < rel_center_y < end_y:
                    color_detected = True

    # Kembalikan True jika setidaknya satu warna terdeteksi
    return color_detected

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height):
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
    cv2.line(frame, (start_x, 0), (start_x, start_y), (255, 0, 0), 2)
    cv2.line(frame, (end_x, 0), (end_x, start_y), (255, 0, 0), 2)
    cv2.line(frame, (start_x, end_y), (start_x, height), (255, 0, 0), 2)
    cv2.line(frame, (end_x, end_y), (end_x, height), (255, 0, 0), 2)
    return frame

def process_frame(frame, start_x, start_y, end_x, end_y, width, height):
    frame = draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height)
    if detect_color_target(frame, start_x, start_y, end_x, end_y):
        print("Target: Warna Terdeteksi")
    return frame

def main_loop(cap, width, height):
    frame = None
    while True:
        frame = capture_frame(cap)
        start_x = cv2.getTrackbarPos('Start X', 'Trackbars')
        start_y = cv2.getTrackbarPos('Start Y', 'Trackbars')
        box_size = cv2.getTrackbarPos('Box Size', 'Trackbars')
        end_x = start_x + box_size
        end_y = start_y + box_size
        frame = process_frame(frame, start_x, start_y, end_x, end_y, width, height)
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('r'):
            reset_position(width, height)

# Fungsi utama
def main():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # cap = cv2.VideoCapture(0)
    time.sleep(2.0)

    frame = capture_frame(cap)
    height, width, _ = frame.shape

    global start_x, start_y, box_size
    box_size = 100
    start_x = int((width - box_size) / 2)
    start_y = int((height - box_size) / 2)

    cv2.namedWindow('Trackbars', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Trackbars', 300, 200)
    cv2.createTrackbar('Start X', 'Trackbars', start_x, width - box_size, on_trackbar_move_horizontal)
    cv2.createTrackbar('Start Y', 'Trackbars', start_y, height - box_size, on_trackbar_move_vertical)
    cv2.createTrackbar('Box Size', 'Trackbars', box_size, min(height, width), on_trackbar_resize)

    main_loop(cap, width, height)

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())

    colorLowerRed = np.array([0, 100, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([160, 100, 100])
    colorUpperRed2 = np.array([180, 255, 255])

    colorLowerBlue = np.array([97, 184, 106])
    colorUpperBlue = np.array([149, 255, 222])

    main()
