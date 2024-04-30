# https://youtu.be/RFqvTmEFtOE
import numpy as np
import cv2
import matplotlib.pyplot as plt

config_file = 'D:\\Yolo\\yolov3.cfg'
frozen_model = 'D:\\Yolo\\yolov3.weights'
# img = cv2.imread('D:\\config\\coding.jpg')
cap = cv2.VideoCapture(0)


model = cv2.dnn_DetectionModel(frozen_model, config_file)
classLabels = []
file_name = 'D:\\config\\labels.txt'
with open(file_name, 'rt') as fpt:
    classLabels = fpt.read().rstrip('\n').split('\n')
    # classLabels.append(fpt.read())
# print(len(classLabels))

model.setInputSize(320, 320)
model.setInputScale(1.0/127.5)  # 255/2 = 127.5
model.setInputMean(127.5)
model.setInputSwapRB(True)

# ------------- image -------------
# ClassIndex, confidece, bbox = model.detect(img, confThreshold=0.5)
# print(ClassIndex)

# font_scale = 3
# font = cv2.FONT_HERSHEY_PLAIN
# for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidece.flatten(), bbox):
#     cv2.rectangle(img, boxes, (255, 0, 0), 2)
#     cv2.putText(img, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40),
#                 font, fontScale=font_scale, color=(0, 255, 0), thickness=3)

# ##img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# ##img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# cv2.imshow('gambar', img)
# cv2.waitKey(0)

# ------------ video ----------------
# if not cap.isOpened():
#     cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     raise IOError("cannot open video")

font_scale = 2
font = cv2.FONT_HERSHEY_PLAIN

while True:
    success, img = cap.read()
    ClassIndex, confidece, bbox = model.detect(img, confThreshold=0.55)

    print(ClassIndex)
    if (len(ClassIndex) != 0):
        for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidece.flatten(), bbox):
            if (ClassInd <= 80):
                cv2.rectangle(img, boxes, (255, 0, 0), 2)
                cv2.putText(img, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40),
                            font, fontScale=font_scale, color=(0, 255, 0), thickness=2)
    cv2.imshow('Object Detection', img)

    if cv2.waitKey(2) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
cap.release()
