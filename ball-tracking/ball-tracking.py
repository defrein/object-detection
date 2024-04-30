# https://pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

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

# warna hijau
colorLower = np.array([29, 86, 6])
colorUpper = np.array([64, 255, 255])

# warna hijau muda (cyan)
# colorLower = np.array([60, 100, 30])
# colorUpper = np.array([80, 255, 255])

# warna merah
# colorLower = np.array([160, 150, 30])
# colorUpper = np.array([190, 255, 255])
# warna merah

colorLower = np.array([0, 0, 0])
colorUpper = np.array([160, 57, 255])

pts = deque(maxlen=args["buffer"])

if not args.get("video", False):
    vs = VideoStream(src=1).start()
else:
    vs = cv2.VideoCapture(args["video"])
time.sleep(2.0)

# terus menerus looping
while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(
        mask.copy(), cv2. RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))

        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
    pts.appendleft(center)

    for i in range(1, len(pts)):
        if pts[i-1] is None or pts[i] is None:
            continue
        thickness = int(np.sqrt(args["buffer"]/float(i+1)) * 2.5)
        cv2.line(frame, pts[i-1], pts[i], (0, 0, 255), thickness)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if not args.get("video", False):
    vs.stop()
else:
    vs.release()

cv2.destroyAllWindows()
