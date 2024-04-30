
import cv2
import numpy as np
import imutils
from imutils.video import WebcamVideoStream
from _thread import *
import time
# set pin GPIO

# move robot function


# drive function
def drive():
    global cx, fw, w, h, minArea, maxArea, flag, lock
    while not threadStop:
        if flag == 1 and lock:
            if cx > 3*fw/4:
                print("Right")
            elif cx < fw/4:
                print("Left")
            elif w*h > maxArea:
                print("Back")
            elif w*h < minArea:
                print("Forward")
        else:
            print("Stop")


def main():
    global cx, w, h, flag, minArea, maxArea, lock, fw, threadStop
    threadStop = False

    lock = False

    flag = 0

    # green color
    lower_color = np.array([29, 86, 6])
    upper_color = np.array([64, 255, 255])

    device = WebcamVideoStream(src=1).start()

    first = True
    start_new_thread(drive, ())

    while True:
        frame = device.read()

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower_color, upper_color)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(
            mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        fh, fw, _ = frame.shape
        cv2.rectangle(frame, (int(fw/4), 0),
                      (int(3*fw/4), fh), (0, 255, 255), 3)

        if len(cnts) > 0:
            # flag = 1
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            x, y, w, h = cv2.boundingRect(c)
            # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            center = (cx, cy)

            if radius > 10 and radius < 100:
                cv2.circle(frame, (int(x), int(y)),
                           int(radius), (255, 0, 0), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                flag = 1
            #cv2.circle(frame, (cx, cy), 3, (0, 255, 255), -1)

            if first:
                maxArea = 3*w*h/2
                minArea = w*h/2

        else:
            flag = 0

        cv2.imshow("Frame", frame)

        k = cv2.waitKey(1) & 0xFF

        if k == ord('q'):
            threadStop = True
            break
        elif k == ord('1') and flag == 1:
            print("Locked")
            print("Fw = ", fw)
            print("Fh = ", fh)
            first = False
            lock = True

    device.stop()
    cv2.destroyAllWindows()


main()
