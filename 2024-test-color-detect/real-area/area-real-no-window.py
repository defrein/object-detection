import cv2
import numpy as np
from collections import deque
import imutils
import argparse
import time



def detect_color_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

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
    detected_coordinates = []

    for cnts, color in [(cnts_red, "Merah")]:
        max_area = 0
        max_contour = None

        for c in cnts:
            area = cv2.contourArea(c)
            if area > max_area:
                max_area = area
                max_contour = c

        if max_contour is not None:
            ((x, y), radius) = cv2.minEnclosingCircle(max_contour)
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                detected_coordinates.append(center)
            else:
                center = (0, 0)

            if radius > 10:
                # cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                # cv2.circle(frame, (center[0], center[1]), 5, (0, 0, 255), -1)

                label_x = center[0] - len(color) * 5
                label_y = center[1] + 20
                # cv2.putText(frame, color, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                color_detected = True

    return color_detected, detected_coordinates

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height):
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
    cv2.line(frame, (0, start_y), (width, start_y), (255, 255, 255), 2)
    return frame
    



def process_frame(frame, start_x, start_y, end_x, end_y, width, height):
    # frame = draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height)
    aksi = ''
    color_detected, coordinates = detect_color_target(frame)
    if color_detected:
        for coord in coordinates:
            print("Koordinat: {}".format(coord))
            if coord[1] < height-box_size:
                aksi = "MAJU"
                # print("Objek berada di atas")
                # send maju
            if coord[0] < width-box_size and coord[1] > height-box_size:
                aksi = "ROTASI KIRI"
                # print("Objek berada di sisi kiri kotak")
                # send belok kiri
            if coord[0] > start_x and coord[1] > height-box_size:
                aksi = "STOP"
                # print("Objek berada di dalam kotak")
                # send stop
    return frame, aksi

def send_to_arduino(aksi):
    # Di sini Anda bisa menambahkan kode untuk mengirimkan aksi ke Arduino
    print("Mengirim aksi ke Arduino:", aksi)


def main_loop(cap, width, height):
    aksi_sebelum = ''
    frame = None
    while True:
        frame = capture_frame(cap)
        box_size = 100
        start_x = width - box_size
        start_y = height - box_size
        end_x = width
        end_y = height
        frame, aksi_sesudah = process_frame(frame, start_x, start_y, end_x, end_y, width, height)

        if aksi_sebelum != aksi_sesudah:
            # Kirim ke Arduino jika aksi sebelumnya tidak sama dengan aksi sesudahnya
            send_to_arduino(aksi_sesudah)
        aksi_sebelum = aksi_sesudah  # Perbarui aksi_sebelum dengan aksi_sesudah saat ini

        # Tampilkan frame jika diperlukan
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break



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
