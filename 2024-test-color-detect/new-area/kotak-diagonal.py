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

def is_below_line(point, line_start, line_end):
    # Dapatkan koordinat x dan y dari titik
    point_x, point_y = point

    # Dapatkan koordinat x dan y dari titik awal dan akhir garis
    line_start_x, line_start_y = line_start
    line_end_x, line_end_y = line_end

    # Hitung persamaan garis y = mx + c
    m = (line_end_y - line_start_y) / (line_end_x - line_start_x)
    c = line_start_y - m * line_start_x

    # Hitung nilai y yang diharapkan pada titik x
    expected_y = m * point_x + c

    # Periksa apakah nilai y titik tersebut lebih besar dari nilai y yang diharapkan
    if point_y > expected_y:
        return True
    else:
        return False

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height):
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

    # Koordinat sudut kiri bawah
    start_x_left_bottom = start_x
    start_y_left_bottom = height

    # Koordinat sudut kanan atas
    start_x_right_top = width
    start_y_right_top = start_y

    # Menggambar garis diagonal dari sudut kiri bawah
    cv2.line(frame, (int(width/2-(box_size+50)), 0), (start_x_left_bottom, start_y_left_bottom), (0, 0, 255), 2)

    # Menggambar garis diagonal dari sudut kanan atas
    cv2.line(frame,  (int(width/2+(box_size+50)), 0), (start_x_right_top, start_y_right_top), (0, 0, 255), 2)
    return frame

def process_frame(frame, start_x, start_y, end_x, end_y, width, height):
    frame = draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height)
    # if detect_color_target(frame, start_x, start_y, end_x, end_y):
    #     print("Target: Warna Terdeteksi")
    return frame

def main_loop(cap, width, height):
    frame = None
    while True:
        frame = capture_frame(cap)
        box_size = 100;
        start_x = width - box_size
        start_y = height - box_size
        end_x = width
        end_y = height
        frame = process_frame(frame, start_x, start_y, end_x, end_y, width, height)
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('r'):
            reset_position(width, height)

# Fungsi utama
def main():
    # cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(0)
    time.sleep(2.0)

    frame = capture_frame(cap)
    height, width, _ = frame.shape

    global box_size
    box_size = 100

    main_loop(cap, width, height)

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())

    # colorLowerRed = np.array([0, 100, 100])
    # colorUpperRed = np.array([20, 255, 255])
    # colorLowerRed2 = np.array([120, 120, 46])
    # colorUpperRed2 = np.array([184, 255, 209])
    
    colorLowerRed = np.array([0, 100, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([0, 187, 0])
    colorUpperRed2 = np.array([107, 255, 255])

    colorLowerBlue = np.array([102, 164, 66])
    colorUpperBlue = np.array([166, 255, 137])

    main()
