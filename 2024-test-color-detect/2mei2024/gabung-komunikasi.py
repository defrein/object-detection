import cv2
import numpy as np
from collections import deque
import imutils
import argparse
import time
from sklearn.mixture import GaussianMixture

# maju cepat = F
# maju sedang = n
# maju lambat = l
#
# muncur cepat = B
# muncur sedang = N
# muncur lambat = b
#
# rotasi 1 kanan = R
# rotasi 2 kanan = r
#
# rotasi 1 kiri = L
# rotasi 2 kiri = l
#
# stop = S
#
# penggiring start = p
# penggiring stop = P

# UNTUK KOMUNIKASI SERIAL
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

STOP = 'S'

PENGGIRING_START = 'p'
PENGGIRING_STOP = 'P'

def detect_color_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Adaptive thresholding
    _, thresh_red1 = cv2.threshold(hsv[:, :, 2], 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, thresh_red2 = cv2.threshold(hsv[:, :, 2], 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, thresh_blue = cv2.threshold(hsv[:, :, 2], 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Apply the thresholding to the HSV ranges
    mask_red1 = cv2.bitwise_and(thresh_red1, thresh_red1, mask=cv2.inRange(hsv, colorLowerRed, colorUpperRed))
    mask_red2 = cv2.bitwise_and(thresh_red2, thresh_red2, mask=cv2.inRange(hsv, colorLowerRed2, colorUpperRed2))
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    mask_blue = cv2.bitwise_and(thresh_blue, thresh_blue, mask=cv2.inRange(hsv, colorLowerBlue, colorUpperBlue))

    # Find contours
    cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_red = imutils.grab_contours(cnts_red)

    cnts_blue = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_blue = imutils.grab_contours(cnts_blue)

    color_detected = False
    detected_coordinates = []
    color_type = []

    for cnts, color in [(cnts_red, "Merah"), (cnts_blue, "Biru")]:
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

                    # label_x = center[0] - len(color) * 5
                    # label_y = center[1] + 20

    if detected_coordinates:
        color_detected = True

    return color_detected, detected_coordinates, color_type

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height):
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
    cv2.line(frame, (0, start_y), (width, start_y), (255, 255, 255), 2)
    return frame

# def process_frame(frame, start_x, start_y, end_x, end_y, width, height):
#     frame = draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height)
#     aksi = ''
#     if stop_detect!= 1:
#         color_detected, coordinates, color_type = detect_color_target(frame)
#         if color_detected:
#             max_x = max(coord[0] for coord in coordinates)
#             max_y = max(coord[1] for coord in coordinates)
            
#             for coord, color in zip(coordinates, color_type):
#                 print("Koordinat: {}".format(coord))
#                 if coord[1] < height - box_size:
#                     aksi = "MAJU"
#                     print("Objek berada di atas")
#                     # send maju
#                 if coord[0] < width - box_size and coord[1] > height - box_size:
#                     aksi = "ROTASI_KIRI"
#                     print("Objek berada di sisi kiri kotak")
#                     # send belok kiri
#                 if coord[0] > start_x and coord[1] > height - box_size:
#                     aksi = "STOP"
#                     print("Objek berada di dalam kotak")
#                     if color == "Merah":
#                         print("MERAH: AMBIL")
#                         break
#                     elif color == "Biru":
#                         print("BIRU: BUANG")
#                         break
#                     # send stop
#                 else:
#                     print("Cari Objek")
#                     aksi = "ROTASI_KIRI"    
#     return frame, aksi

def process_frame(frame, start_x, start_y, end_x, end_y, width, height):
    frame = draw_rectangle(frame, start_x, start_y, end_x, end_y, width, height)
    aksi = ''
    if stop_detect!= 1:
        color_detected, coordinates, color_type = detect_color_target(frame)
        if color_detected:
            max_x = max(coord[0] for coord in coordinates)
            max_y = max(coord[1] for coord in coordinates)
            
            for coord, color in zip(coordinates, color_type):
                print("Koordinat: {}".format(coord))
                if color == "Merah":
                    if coord[1] < height - box_size:
                        aksi = "MAJU"
                        print("Objek berada di atas")
                    elif coord[0] < width - box_size and coord[1] > height - box_size:
                        aksi = "ROTASI_KIRI"
                        print("Objek berada di sisi kiri kotak")
                    elif coord[0] > start_x and coord[1] > height - box_size:
                        aksi = "STOP"
                        print("Objek berada di dalam kotak")
                        print("MERAH: AMBIL")
                        break
                    else:
                        print("Cari Objek")
                        aksi = "CARI_OBJEK"
                elif color == "Biru" and coord[0] > start_x and coord[1] > height - box_size:
                    aksi = "STOP"
                    print("Objek berada di dalam kotak")
                    print("BIRU: BUANG")
                    break
                else:
                    continue
    return frame, aksi

def send_to_arduino(aksi):
    # Di sini Anda bisa menambahkan kode untuk mengirimkan aksi ke Arduino
    if aksi == 'MAJU':
        var = MAJU_SEDANG  # Misalnya, 'M' adalah perintah untuk maju
        ser.write(var.encode('utf-8'))
    elif aksi == 'ROTASI_KIRI':
        var = ROTASI_KIRI_CEPAT  # Misalnya, 'N' adalah perintah untuk mundur
        ser.write(var.encode('utf-8'))
    elif aksi == 'CARI_OBJEK':
        var = ROTASI_KIRI_LAMBAT  # Misalnya, 'N' adalah perintah untuk mundur
        ser.write(var.encode('utf-8'))
    elif aksi == 'STOP':
        var = STOP  # Misalnya, 'N' adalah perintah untuk mundur
        ser.write(var.encode('utf-8'))
    # Tambahkan elif untuk aksi lainnya jika diperlukan
    else:
        print("Aksi tidak dikenali:", aksi)

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
            if(aksi_sesudah != 'STOP'):
                # send_to_arduino(aksi_sesudah)
                stop_detect = 0
            else:
                stop_detect = 1
            # print('send')
        aksi_sebelum = aksi_sesudah
        
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break



# Fungsi utama
def main():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # cap = cv2.VideoCapture(-1)
    time.sleep(2.0)

    frame = capture_frame(cap)
    height, width, _ = frame.shape

    global box_size, stop_detect
    stop_detect = 0
    box_size = 100

    main_loop(cap, width, height)

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())
    # ser = serial.Serial('/dev/ttyACM0', 115200)

    # colorLowerRed = np.array([0, 100, 100])
    # colorUpperRed = np.array([20, 255, 255])
    # colorLowerRed2 = np.array([120, 120, 46])
    # colorUpperRed2 = np.array([184, 255, 209])
    colorLowerRed = np.array([0, 150, 100])
    colorUpperRed = np.array([5, 255, 255])
    colorLowerRed2 = np.array([160, 150, 100])
    colorUpperRed2 = np.array([180, 255, 255])
    
    # colorLowerRed = np.array([148, 194, 62])
    # colorUpperRed = np.array([255, 255, 255])
    # colorLowerRed2 = np.array([0, 187, 0])
    # colorUpperRed2 = np.array([107, 255, 255])

    # colorLowerRed = np.array([0, 100, 100])
    # colorUpperRed = np.array([10, 255, 255])
    # colorLowerRed2 = np.array([160, 100, 100])
    # colorUpperRed2 = np.array([180, 255, 255])


    colorLowerBlue = np.array([102, 164, 66])
    colorUpperBlue = np.array([166, 255, 137])

    main()
