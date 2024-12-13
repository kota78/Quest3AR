#!/usr/bin/env python3
# coding: utf-8

import cv2
import numpy as np
from cv2 import aruco
import sys
args = sys.argv

# Size and offset value
size = 150
offset = 10
x_offset = y_offset = int(offset) // 2
id=int(args[1]) if len(args) > 1 else 0

# get dictionary and generate image
dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
ar_img = aruco.generateImageMarker(dictionary, id, size)

# make white image
img = np.zeros((size + offset, size + offset), dtype=np.uint8)
img += 255

# overlap image
img[y_offset:y_offset + ar_img.shape[0], x_offset:x_offset + ar_img.shape[1]] = ar_img

cv2.imwrite(f"marker_{id}.png", img)
