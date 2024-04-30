# algoritma deteksi bola by DEF

# object:n warna hijau
# bisa menampilkan data: yes
# bisa menentukan arah: yes
# motor: no
# servo: no
# sensor: no

from sre_constants import SUCCESS
import cv2
import numpy as np
import time

# warna hijau
colorLower = np.array([29, 86, 6])
colorUpper = np.array([64, 255, 255])

cp = cv2.VideoCapture(0)

while True:
    success, video = cp.read()
