import cv2
import numpy as np
import imutils
import argparse
import time
import serial

# Constants for serial communication
MAJU_CEPAT = 'F'
MAJU_SEDANG = 'n'
MAJU_LAMBAT = 'l'

MUNDUR_CEPAT = 'B'
MUNDUR_SEDANG = 'n'
MUNDUR_LAMBAT = 'b'

ROTASI_KANAN_CEPAT = 'R'
ROTASI_KANAN_LAMBAT = 'r'

ROTASI_KIRI_CEPAT = 'L'
ROTASI_KIRI_LAMBAT = 'l'

STOP = 's'

PENGGIRING_START = 'p'
PENGGIRING_STOP = 'P'

# warna
MERAH = 'Merah'
BIRU = 'Biru'

# status
MENCARI = 1
DAPAT_MERAH = 2
DAPAT_BIRU = 2
SELESAI = 4

# Global variables
global box_size, stop_detect, width, height
width = 0
height = 0
stop_detect = False
box_size = 100

def main():
    global width, height
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # cap = cv2.VideoCapture(-1)
    time.sleep(2.0)

    frame = capture_frame(cap)
    height, width, _ = frame.shape

    main_loop(cap)

    cv2.destroyAllWindows()
    cap.release()

def main_loop(cap):
    global status
    status = ''
    aksi_sebelum = ''
    frame = None
    stop_detect = False
    # looping
    while True:
        frame = capture_frame(cap)
        box_size = 100
        start_x = width - box_size
        start_y = height - box_size
        end_x = width
        end_y = height
        if not stop_detect:
            frame, aksi_sesudah, status = process_frame(frame, start_x, start_y, end_x, end_y, stop_detect)

            if aksi_sebelum != aksi_sesudah:
                if aksi_sesudah == STOP:
                    if status == DAPAT_BIRU:
                        time.sleep(3)
                        stop_detect = False
                    if status == DAPAT_MERAH:
                        stop_detect = True
                    
                    # send something
                else:
                    stop_detect = False
                print('send')
                print(stop_detect)
            aksi_sebelum = aksi_sesudah
        
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y):
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
    cv2.line(frame, (0, start_y), (width, start_y), (255, 255, 255), 2)
    return frame

def process_frame(frame, start_x, start_y, end_x, end_y, stop_detect):
    global status
    status = ''
    frame = draw_rectangle(frame, start_x, start_y, end_x, end_y)
    aksi = ''
    if stop_detect == 0:
        color_detected, coordinates, color_type = detect_color_target(frame)
        if color_detected:
            max_x = max(coord[0] for coord in coordinates)
            max_y = max(coord[1] for coord in coordinates)
            
            for coord, color in zip(coordinates, color_type):
                print("Koordinat: {}".format(coord))
                if color == MERAH:
                    if coord[1] < height - box_size:
                        aksi = MAJU_CEPAT
                        print("Objek berada di atas")
                    elif coord[0] < width - box_size and coord[1] > height - box_size:
                        aksi = ROTASI_KIRI_LAMBAT
                        print("Objek berada di sisi kiri kotak")
                    elif coord[0] > start_x and coord[1] > height - box_size:
                        status = DAPAT_MERAH
                        print("Objek berada di dalam kotak")
                        print("MERAH: AMBIL")
                        break
                    else:
                        print("Cari Objek")
                        aksi = ROTASI_KIRI_LAMBAT
                        status = MENCARI
                elif color == BIRU and coord[0] > start_x and coord[1] > height - box_size:
                    status = DAPAT_BIRU
                    print("Objek berada di dalam kotak")
                    print("BIRU: BUANG")
                    break
                else:
                    continue
    return frame, aksi, status

def detect_color_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(hsv, colorLowerRed, colorUpperRed)
    mask_red2 = cv2.inRange(hsv, colorLowerRed2, colorUpperRed2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel=np.ones((10, 10), np.uint8))
    mask_red = cv2.dilate(mask_red, kernel=np.ones((15, 15), np.uint8))

    mask_blue = cv2.inRange(hsv, colorLowerBlue, colorUpperBlue)
    mask_blue = cv2.erode(mask_blue, None, iterations=2)
    mask_blue = cv2.dilate(mask_blue, None, iterations=2)

    cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_red = imutils.grab_contours(cnts_red)

    cnts_blue = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_blue = imutils.grab_contours(cnts_blue)

    color_detected = False
    detected_coordinates = []
    color_type = []

    for cnts, color in [(cnts_red, MERAH), (cnts_blue, BIRU)]:
        for c in cnts:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 10:
                M = cv2.moments(c)
                if M["m00"]!= 0:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    detected_coordinates.append(center)
                    color_type.append(color)
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, (center[0], center[1]), 5, (0, 0, 255), -1)

    if detected_coordinates:
        color_detected = True

    return color_detected, detected_coordinates, color_type

def send_to_arduino(aksi):
        ser.write(aksi.encode('utf-8'))
        print("Dikirim:", aksi)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())

    # Serial communication setup
    # ser = serial.Serial('/dev/ttyACM0', 115200)
    # ser = serial.Serial('COM7', 115200)

    # Define HSV color ranges
    colorLowerRed = np.array([0, 200, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([160, 200, 100])
    colorUpperRed2 = np.array([180, 255, 255])

    colorLowerBlue = np.array([102, 164, 66])
    colorUpperBlue = np.array([166, 255, 137])

    main()
