import common as cm
import cv2
import numpy as np
from PIL import image
import time
from threading import Thread

cap = cv2.VideoCapture(0)
threshold = 0.2
top_k = 5  # number of objects to be shown as detected

model_dir = 'D:\\config\\all_models'
model = 'mobilenet_ssd_v2_coco_quant_postprocess.tflite'
model_edgetpu = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
lbl = 'coco_labels.txt'

tolerance = 0.1
x_deviation = 0
y_deviation = 0
arr_track_data = [0, 0, 0, 0, 0, 0]

arr_valid_objects = ['apple', 'sports ball',
                     'frisbee', 'orange', 'mouse', 'vase', 'banana']


def track_object(objs, labels):
    # global delay
    global x_deviation, y_deviation, tolerance, arr_track_data

    if(len(objs) == 0):
        print("no objects to track")
        # ut.stop()
        return

    k = 0
    flag = 0
    for obj in objs:
        lbl = labels.get(obj.id, obj.id)
        k = arr_valid_objects.count(lbl)
        if (k > 0):
            x_min, y_min, x_max, y_max = list(obj.bbox)
            flag = 1
            break

    # print(x_min, y_min, x_max, y_max)
    if (flag == 0):
        print("selected object no present")
        return

    x_diff = x_max-x_min
    y_diff = y_max-y_min
    print("x_diff ", round(x_diff, 5))
    print("y_diff ", round(y_diff, 5))

    obj_x_center = x_min+(x_diff/2)
    obj_x_center = round(obj_x_center, 3)
    obj_y_center = y_min+(y_diff/2)
    obj_y_center = round(obj_y_center, 3)
    #print("[",obj_x_center, obj_y_center,"]")

    x_deviation = round(0.5-obj_x_center, 3)
    y_deviation = round(0.5-obj_y_center, 3)
    print("{", x_deviation, y_deviation, "}")

    # and the move the robot

    arr_track_data[0] = obj_x_center
    arr_track_data[1] = obj_y_center
    arr_track_data[2] = x_deviation
    arr_track_data[3] = y_deviation


def move_robot():
    global x_deviation, y_deviation, tolerance, arr_track_data
    print("robot moving")
    print(x_deviation, y_deviation, tolerance, arr_track_data)

    if(abs(x_deviation) < tolerance and abs(y_deviation) < tolerance):
        cmd = "Stop"
        delay1 = 0
        print("red light ON")

    else:
        print("red light OFF")
        if (abs(x_deviation) > abs(y_deviation)):
            if(x_deviation >= tolerance):
                cmd = "Move Left"
            if(x_deviation <= -1*tolerance):
                cmd = "Move Right"
        else:
            if(y_deviation >= tolerance):
                cmd = "Move Forward"
            if(y_deviation >= -1*tolerance):
                cmd = "Move Backward"
    arr_track_data[4] = cmd
    arr_track_data[5] = delay1


def main():

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2_im = frame
        cv2_im = cv2.flip(cv2_im, 0)
        cv2_im = cv2.flip(cv2_im, 1)

        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
