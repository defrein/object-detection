# https://youtu.be/cMJwqxskyek
# https://github.com/CreepyD246/Simple-Color-Detection-with-Python-OpenCV/blob/main/color_detection.py

# Importing all modules
import cv2
import numpy as np

# Specifying upper and lower ranges of color to detect in hsv format
lower = np.array([29, 86, 6])
upper = np.array([64, 255, 255])  # (These ranges will detect Greenq)

# Capturing webcam footage
webcam_video = cv2.VideoCapture(0)

while True:
    success, video = webcam_video.read()  # Reading webcam footage

    # Converting BGR image to HSV format
    img = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)

    # Masking the image to find our color
    mask = cv2.inRange(img, lower, upper)

    mask_contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Finding contours in mask image

    # Finding position of all contours
    if len(mask_contours) != 0:
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > 500:
                x, y, w, h = cv2.boundingRect(mask_contour)
                cv2.rectangle(video, (x, y), (x + w, y + h),
                              (0, 0, 255), 3)  # drawing rectangle

    cv2.imshow("mask image", mask)  # Displaying mask image

    cv2.imshow("window", video)  # Displaying webcam image

    cv2.waitKey(1)
