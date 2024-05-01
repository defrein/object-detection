import cv2
import numpy as np
from collections import deque
import imutils
import argparse
import time

def main():
    global frame_width, frame_height, start_x, start_y, box_size, end_x, end_y
    
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    time.sleep(2.0)

    frame = capture_frame(cap)
    frame_height, frame_width, _ = frame.shape  # Fix the order of dimensions

    box_size = 100
    start_x = frame_width - box_size
    start_y = frame_height - box_size
    end_x = frame_width
    end_y = frame_height

    main_loop(cap)  # Remove passing frame_width and frame_height

    cv2.destroyAllWindows()
    cap.release()

def capture_frame(cap):
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    return frame

def draw_rectangle(frame):
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)
    return frame

def draw_diagonal(frame):
    start_x_left_bottom = start_x
    start_y_left_bottom = frame_height

    start_x_right_top = frame_width
    start_y_right_top = start_y

    cv2.line(frame, (int(frame_width/2-(box_size+50)), 0), (start_x_left_bottom, start_y_left_bottom), (0, 0, 255), 2)
    cv2.line(frame,  (int(frame_width/2+(box_size+50)), 0), (start_x_right_top, start_y_right_top), (0, 0, 255), 2)

def draw_cross(frame):
    cv2.line(frame, (int(frame_width/2), 0), (int(frame_width/2), frame_height),  (255, 255, 255), 2)
    cv2.line(frame, (0, int(frame_height/2)), (frame_width, int(frame_height/2)), (255,255,255), 2)


def process_frame(frame):
    frame = draw_rectangle(frame)
    frame = draw_diagonal(frame)
    frame = draw_cross(frame)

def main_loop(cap):
    frame = None
    while True:
        frame = capture_frame(cap)
        end_x = frame_width
        end_y = frame_height
        frame = process_frame(frame)
        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-v")
    args = vars(ap.parse_args())

    colorLowerRed = np.array([0, 100, 100])
    colorUpperRed = np.array([10, 255, 255])
    colorLowerRed2 = np.array([0, 187, 0])
    colorUpperRed2 = np.array([107, 255, 255])

    colorLowerBlue = np.array([102, 164, 66])
    colorUpperBlue = np.array([166, 255, 137])

    main()

