#multiple ball tracking

from collections import deque
from tkinter import CENTER
from tkinter.messagebox import NO
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# menguraikan argumen
ap = argparse.ArgumentParser()
# ap.add_argument("-v", "--video", help="path to the (optional) video file")
ap.add_argument("-v")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# # warna merah
# colorLowerRed = np.array([156, 134, 116])
# colorUpperRed = np.array([193, 227, 170])

# Warna merah
colorLowerRed = np.array([0, 100, 100])
colorUpperRed = np.array([10, 255, 255])
colorLowerRed2 = np.array([160, 100, 100])
colorUpperRed2 = np.array([180, 255, 255])

# warna biru
colorLowerBlue = np.array([97, 184, 106])
colorUpperBlue = np.array([149, 255, 222])

# # warna putih
# colorLowerWhite = np.array([97, 23, 120])
# colorUpperWhite = np.array([149, 184, 231])

pts = deque(maxlen=args["buffer"])

if not args.get("video", False):
    vs = VideoStream(src=1).start()
else:
    vs = cv2.VideoCapture(args["video"])
time.sleep(2.0)

# Terus menerus looping
while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

     # Deteksi warna merah
    mask_red1 = cv2.inRange(hsv, colorLowerRed, colorUpperRed)
    mask_red2 = cv2.inRange(hsv, colorLowerRed2, colorUpperRed2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_red = cv2.erode(mask_red, None, iterations=2)
    mask_red = cv2.dilate(mask_red, None, iterations=2)

    # Deteksi warna biru
    mask_blue = cv2.inRange(hsv, colorLowerBlue, colorUpperBlue)
    mask_blue = cv2.erode(mask_blue, None, iterations=2)
    mask_blue = cv2.dilate(mask_blue, None, iterations=2)

    # Deteksi warna putih
    # mask_white = cv2.inRange(hsv, colorLowerWhite, colorUpperWhite)
    # mask_white = cv2.erode(mask_white, None, iterations=2)
    # mask_white = cv2.dilate(mask_white, None, iterations=2)

    # Gabungkan mask untuk ketiga warna
    mask_combined = cv2.bitwise_or(mask_red, mask_blue)
    # mask_combined = cv2.bitwise_or(mask_combined, mask_white)

    cnts = cv2.findContours(mask_combined.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # Loop melalui kontur yang terdeteksi
    for c in cnts:
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] != 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        else:
            center = (0, 0)

        # Jika radius lebih besar dari 10, gambar lingkaran dan centernya
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    # Tampilkan bingkai hasil
    cv2.imshow("Frame", frame)

    # Periksa tombol 'q' untuk keluar dari loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan
if not args.get("video", False):
    vs.stop()
else:
    vs.release()

cv2.destroyAllWindows()
