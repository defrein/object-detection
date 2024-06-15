import threading
import time
import serial
import cv2
import numpy as np
import imutils

# Constants for serial communication
MAJU_CEPAT = 'F'
MAJU_SEDANG = 'n'
MAJU_LAMBAT = 'f'

MUNDUR_CEPAT = 'B'
MUNDUR_SEDANG = 'N'
MUNDUR_LAMBAT = 'b'

ROTASI_KANAN_CEPAT = 'R'
ROTASI_KANAN_LAMBAT = 'r'

ROTASI_KIRI_CEPAT = 'L'
ROTASI_KIRI_LAMBAT = 'l'

STOP = 's'

PENGGIRING_START = 'p'
PENGGIRING_STOP = 'P'

SELESAI_DETECT = 'K'
MULAI_DETECT = 'k'

# sensor ir
INFRARED = 'i'

# warna
MERAH = 'Merah'
BIRU = 'Biru'

# status
MENCARI = 1
DAPAT_MERAH = 2
DAPAT_BIRU = 3
SELESAI = 4
TIDAK_ADA = 5

#led 
LED_START = 'Z'
LED_RETRY = 'z'


# Global variables
global box_size, stop_detect, width, height, sensor_atas, dilateMorphBlue
width = 0
height = 0
stop_detect = False
box_size = 100
dilateMorphBlue = None
def main():
    global width, height
    # cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(-1)
    # cap = cv2.VideoCapture(0)
    time.sleep(2.0)

    frame = capture_frame(cap)
    height, width, _ = frame.shape
    main_loop(cap)

    cv2.destroyAllWindows()
    cap.release()

def main_loop(cap):
    global status, sensor_atas, stop_detect
    sensor_atas = '1'
    status = MENCARI
    aksi_sebelum = ''
    frame = None
    stop_detect = True
    warna = ''

    # Create and start the receiver thread
    receiver_thread = threading.Thread(target=receive_from_arduino, daemon=True)
    receiver_thread.start()
    # looping
    while True:
        frame = capture_frame(cap)
        box_size = 100
        start_x = width - box_size
        start_y = height - box_size
        end_x = width
        end_y = height
        if not stop_detect:
            frame, aksi_sesudah, status, dilateMorphBlue = process_frame(frame, start_x, start_y, end_x, end_y, stop_detect)
            print('status ' + str(status))

            if sensor_atas == 0:
                stop_detect = False
                print("Sensor atas terdeteksi!")
                if warna == BIRU:
                    # print('hahahahhabiru')
                    sensor_atas = 1
                    pass
                elif warna == MERAH:
                    # print('hahahahha')
                    send_to_arduino(MUNDUR_LAMBAT)
                    time.sleep(1.5)
                    send_to_arduino(PENGGIRING_STOP)
                    send_to_arduino(SELESAI_DETECT)
                    stop_detect = True
                sensor_atas = 1

            if aksi_sebelum != aksi_sesudah:
                if status == DAPAT_BIRU:
                    print('Dapat biru')
                    aksi_sesudah = PENGGIRING_START
                    send_to_arduino(aksi_sesudah)
                    warna = BIRU
                    if sensor_atas == 0:
                        print('kedetek bola')
                elif status == DAPAT_MERAH:
                    print('Dapat merah')
                    aksi_sesudah = PENGGIRING_START
                    send_to_arduino(aksi_sesudah)
                    warna = MERAH
                    if sensor_atas == 0:
                        send_to_arduino(MUNDUR_LAMBAT)
                        send_to_arduino(STOP)
                        time.sleep(1.5)
                        send_to_arduino(PENGGIRING_STOP)
                        send_to_arduino(SELESAI_DETECT)
                        stop_detect = False
                        
                    
                elif status == MENCARI:
                    send_to_arduino(aksi_sesudah)
                    pass
            aksi_sebelum = aksi_sesudah

        # cv2.imshow('Camera', frame)
        # cv2.imshow('Blue', dilateMorphBlue)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y):
    cv2.line(frame, (width//2 - box_size//2, 0), (width//2 - box_size//2, height), (255, 0, 0), 2)
    cv2.line(frame, (width//2 + box_size//2, 0), (width//2 + box_size//2, height), (255, 0, 0), 2)
    cv2.line(frame, (0, height - box_size), (width, height - box_size), (255, 255, 0), 2)
    cv2.rectangle(frame, (width//2 - box_size//2, height - box_size), (width//2 + box_size//2, height), (0, 255, 0), 2)
    return frame

def process_frame(frame, start_x, start_y, end_x, end_y, stop_detect):
    global status
    status = ''
    frame = draw_rectangle(frame, start_x, start_y, end_x, end_y)
    aksi = ''
    if stop_detect == 0:
        color_detected, coordinates, color_type, dilateMorphBlue = detect_color_target(frame, start_x, start_y)
        if color_detected:
            for coord, color in zip(coordinates, color_type):
                # print("Koordinat: {}".format(coord))
                if color == MERAH:
                    if coord[1] <= height - box_size:
                        status = MENCARI
                        aksi = MAJU_SEDANG
                        print("Objek berada di atas")
                    elif coord[0] < width//2 - box_size//2 and coord[1] > height - box_size:
                        status = MENCARI
                        aksi = ROTASI_KIRI_LAMBAT
                        print('KIRI')
                    elif coord[0] > width//2 + box_size//2 and coord[1] > height - box_size:
                        status = MENCARI
                        aksi = ROTASI_KANAN_LAMBAT
                        print("Objek berada di kanan")
                    elif (coord[0] >= width//2 - box_size//2 and coord[0] <= width//2 - box_size//2)  and coord[1] > height - box_size:
                        status = DAPAT_MERAH
                        aksi = PENGGIRING_START
                        # print("Objek berada di dalam kotak")
                        print("MERAH: AMBIL")
                        break
                    else:
                        print("Cari Objek")
                        status = TIDAK_ADA
                        send_to_arduino(MUNDUR_LAMBAT)
                        time.sleep(1)
                elif color == BIRU and (coord[0] >= width//2 - box_size//2 and coord[0] <= width//2 - box_size//2)  and coord[1] > height - box_size:
                    status = DAPAT_BIRU
                    aksi = PENGGIRING_START
                    print("BIRU: BUANG")
                    break
    return frame, aksi, status, dilateMorphBlue

def detect_color_target(frame, start_x, start_y):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(hsv, colorLowerRed, colorUpperRed)
    mask_red2 = cv2.inRange(hsv, colorLowerRed2, colorUpperRed2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel=np.ones((10, 10), np.uint8))
    mask_red = cv2.dilate(mask_red, kernel=np.ones((15, 15), np.uint8))

    mask_blue = cv2.inRange(hsv, colorLowerBlue, colorUpperBlue)
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel=np.ones((10, 10), np.uint8))
    dilateMorphBlue = cv2.dilate(mask_blue, kernel=np.ones((15, 15), np.uint8))

    cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_red = imutils.grab_contours(cnts_red)

    cnts_blue = cv2.findContours(dilateMorphBlue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_blue = imutils.grab_contours(cnts_blue)

    color_detected = False
    detected_coordinates = []
    color_type = []

    max_area_red = 0
    max_contour_red = None
    max_area_blue = 0
    max_contour_blue = None

    for c in cnts_red:
        area = cv2.contourArea(c)
        if area > max_area_red:
            max_area_red = area
            max_contour_red = c
            # print(max_contour_red)
    
    for c in cnts_blue:
        area = cv2.contourArea(c)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 10:
            M = cv2.moments(c)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if center[0] > start_x and center[1] > height - box_size:
                    if area > max_area_blue:
                        max_area_blue = area
                        max_contour_blue = c

    if max_contour_red is not None:
        ((x, y), radius) = cv2.minEnclosingCircle(max_contour_red)
        if radius > 10:
            M = cv2.moments(max_contour_red)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                detected_coordinates.append(center)
                color_type.append(MERAH)
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, (center[0], center[1]), 5, (0, 0, 255), -1)
                color_detected = True
    
    if max_contour_blue is not None:
        ((x, y), radius) = cv2.minEnclosingCircle(max_contour_blue)
        if radius > 10:
            M = cv2.moments(max_contour_blue)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                detected_coordinates.append(center)
                color_type.append(BIRU)
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, (center[0], center[1]), 5, (0, 0, 255), -1)
                color_detected = True

    for c in cnts_blue:
        area = cv2.contourArea(c)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 30:
            M = cv2.moments(c)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if center[0] > start_x and center[1] > height - box_size:
                    detected_coordinates.append(center)
                    color_type.append(BIRU)
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, (center[0], center[1]), 5, (0, 0, 255), -1)
                    color_detected = True

    return color_detected, detected_coordinates, color_type, dilateMorphBlue

def send_to_arduino(aksi):
    ser.write(aksi.encode('utf-8'))
    print("Dikirim:", aksi)

def receive_from_arduino():
    global sensor_atas, stop_detect
    sensor_atas = ''
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"Data dari Arduino: {data}")
            if data == INFRARED:
                sensor_atas = 0
            if data == MULAI_DETECT:
                stop_detect = False
            if data == "RESET":
                stop_detect = True
            if data == "ON_START":
                send_to_arduino(LED_START)
            if data == "ON_RETRY":
                send_to_arduino(LED_RETRY)
            
        

if _name_ == "_main_":
    # Serial communication setup
    ser = serial.Serial('/dev/ttyACM0', 115200)
    # ser = serial.Serial('COM7', 115200)

    # red
    colorLowerRed = np.array([0, 150, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([160, 150, 100])
    colorUpperRed2 = np.array([180, 255, 255])

    # blue
    # colorLowerBlue = np.array([102, 164, 66])
    # colorUpperBlue = np.array([166, 255, 137])

    # ungu
    # colorLowerBlue = np.array([121, 64, 107])
    # colorUpperBlue = np.array([160, 255, 255])
    # colorLowerBlue = np.array([95, 78, 53])
    # colorUpperBlue = np.array([127, 255, 255])

    # ungu malam dekat
    colorLowerBlue = np.array([120, 50, 50])
    colorUpperBlue = np.array([135, 255, 255])
    # colorLowerBlue = np.array([120, 0, 0])
    # colorUpperBlue = np.array([160, 255, 255])

    # ungu siang dekat
    # colorLowerBlue = np.array([119, 0, 25])
    # colorUpperBlue = np.array([178, 255, 255])


    main()