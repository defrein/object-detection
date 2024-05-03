#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USAGE: You need to specify a filter and "only one" image source
#
# (python) range-detector --filter RGB --image /path/to/image.png
# or
# (python) range-detector --filter HSV --webcam

import cv2
import argparse
from operator import xor
import numpy as np


def callback(value):
    pass


def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--filter', required=True,
                    help='Range filter. RGB or HSV')
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    args = vars(ap.parse_args())

    if not xor(bool(args['image']), bool(args['webcam'])):
        ap.error("Please specify only one image source")

    if not args['filter'].upper() in ['RGB', 'HSV']:
        ap.error("Please speciy a correct filter.")

    return args


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values


def main():
    dilateMorpholgy = 0
    args = get_arguments()

    range_filter = args['filter'].upper()

    if args['image']:
        image = cv2.imread(args['image'])

        if range_filter == 'RGB':
            frame_to_thresh = image.copy()
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            # morpholgy = cv2.morphologyEx(frame_to_thresh, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))
            # morpholgy = cv2.morphologyEx(morpholgy, cv2.MORPH_CLOSE, kernel=np.ones((10, 10), np.uint8))
            dilateMorpholgy = cv2.dilate(frame_to_thresh, kernel=np.ones((15, 15), np.uint8))
    else:
        camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    setup_trackbars(range_filter)

    # Inisialisasi variabel thresh di luar loop while
    thresh = None

    while True:
        if args['webcam']:
            ret, image = camera.read()

            if not ret:
                break

            if range_filter == 'RGB':
                frame_to_thresh = image.copy()
            else: 
                frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Terapkan operasi morfologi pada gambar yang telah di-threshold
            if thresh is not None:
                morpholgy = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))
                morpholgy = cv2.morphologyEx(morpholgy, cv2.MORPH_CLOSE, kernel=np.ones((10, 10), np.uint8))
                dilateMorpholgy = cv2.dilate(morpholgy, kernel=np.ones((15, 15), np.uint8))

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)

        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        if args['preview']:
            if range_filter == 'HSV':
                # Tampilkan hasil operasi morfologi bersamaan dengan gambar hasil threshold
                preview = cv2.bitwise_and(image, image, mask=thresh)
                preview = cv2.bitwise_and(preview, preview, mask=dilateMorpholgy)
                cv2.imshow("Preview", np.hstack([cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR), preview]))
        else:
            cv2.imshow("Original", image)
            cv2.imshow("Thresh", thresh)
            cv2.imshow("Morphology", dilateMorpholgy)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break





if __name__ == '__main__':
    main()