import threading
import time
import serial
import cv2
import numpy as np
import imutils

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

# Global variables
global box_size, stop_detect, width, height, sensor_atas
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
    global status, sensor_atas
    sensor_atas = '1'
    status = MENCARI
    aksi_sebelum = ''
    frame = None
    stop_detect = False
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
            frame, aksi_sesudah, status = process_frame(frame, start_x, start_y, end_x, end_y, stop_detect)
            print('status ' + str(status))

            if sensor_atas == 0:
                stop_detect = False
                # send_to_arduino(PENGGIRING_STOP)
                print("Sensor atas terdeteksi!")
                if warna == BIRU:
                    print('hahahahhabiru')
                    pass
                if warna == MERAH:
                    print('hahahahha')
                    send_to_arduino(PENGGIRING_STOP)
                    stop_detect = True
                sensor_atas = 1

            if aksi_sebelum != aksi_sesudah:
                # if sensor_atas == 0:
                #     send_to_arduino(PENGGIRING_STOP)
                #     print("Sensor atas terdeteksi!")
                #     stop_detect = False
                #     break

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
                        send_to_arduino(PENGGIRING_STOP)
                        stop_detect = False
                        print('kedetek bola')
                    # time.sleep(3)
                        # stop_detect = True
                        # break
                    # else:
                    #     stop_detect  = False
                    # send_to_arduino(STOP)
                    # send_to_arduino(PENGGIRING_STOP)
                    
                # elif status == MENCARI:
                #     # send_to_arduino(aksi_sesudah)
                #     pass
                # print('Send')
                # print('Stop detect = ' + str(stop_detect))
            aksi_sebelum = aksi_sesudah

        # if sensor_atas == 0:
        #     print("Sensor atas terdeteksi!")
        #     send_to_arduino(STOP)
        
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame, start_x, start_y, end_x, end_y):
    cv2.line(frame, (0, start_y), (width-box_size, start_y), (255, 255, 255), 2)
    cv2.line(frame, (width-box_size, 0), (width-box_size, height-box_size), (255, 255, 255), 2)
    cv2.line(frame, (0 + box_size, 0), (0 + box_size, height - box_size), (255, 255, 255), 2)
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
    return frame

def process_frame(frame, start_x, start_y, end_x, end_y, stop_detect):
    global status
    status = ''
    frame = draw_rectangle(frame, start_x, start_y, end_x, end_y)
    aksi = ''
    if stop_detect == 0:
        color_detected, coordinates, color_type = detect_color_target(frame, start_x, start_y)
        if color_detected:
            for coord, color in zip(coordinates, color_type):
                # print("Koordinat: {}".format(coord))
                if color == MERAH:
                    if coord[0] < width - box_size and coord[1] < height - box_size:
                        status = MENCARI
                        aksi = MAJU_CEPAT
                        # print("Objek berada di atas")
                    elif coord[0] > width - box_size and coord[1] < height - box_size:
                        status = MENCARI
                        aksi = ROTASI_KANAN_LAMBAT
                        # print("Objek berada di kanan")
                    elif coord[0] < width - box_size and coord[1] > height - box_size:
                        status = MENCARI
                        aksi = ROTASI_KIRI_LAMBAT
                        # print("Objek berada di sisi kiri kotak")
                    elif coord[0] > start_x and coord[1] > height - box_size:
                        status = DAPAT_MERAH
                        aksi = PENGGIRING_START
                        # print("Objek berada di dalam kotak")
                        print("MERAH: AMBIL")
                        break
                    else:
                        print("Cari Objek")
                        aksi = MAJU_LAMBAT
                        status = MENCARI
                elif color == BIRU and coord[0] > start_x and coord[1] > height - box_size:
                    status = DAPAT_BIRU
                    aksi = PENGGIRING_START
                    # print("Objek berada di dalam kotak")
                    print("BIRU: BUANG")
                    break
    return frame, aksi, status

def detect_color_target(frame, start_x, start_y):
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

    max_area_red = 0
    max_contour_red = None
    max_area_blue = 0
    max_contour_blue = None

    for c in cnts_red:
        area = cv2.contourArea(c)
        if area > max_area_red:
            max_area_red = area
            max_contour_red = c

    for c in cnts_blue:
        area = cv2.contourArea(c)
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
                if center[0] > start_x and center[1] > height - box_size:
                    detected_coordinates.append(center)
                    color_type.append(BIRU)
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, (center[0], center[1]), 5, (0, 0, 255), -1)
                    color_detected = True

    return color_detected, detected_coordinates, color_type

def send_to_arduino(aksi):
    ser.write(aksi.encode('utf-8'))
    print("Dikirim:", aksi)

def receive_from_arduino():
    global sensor_atas
    sensor_atas = ''
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"Data dari Arduino: {data}")
            if data == INFRARED:
                sensor_atas = 0
            

if __name__ == "__main__":
    # Serial communication setup
    # ser = serial.Serial('/dev/ttyACM0', 115200)
    ser = serial.Serial('COM7', 115200)

    # Define HSV color ranges
    colorLowerRed = np.array([0, 150, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([160, 150, 100])
    colorUpperRed2 = np.array([180, 255, 255])

    colorLowerBlue = np.array([102, 164, 66])
    colorUpperBlue = np.array([166, 255, 137])

    main()
