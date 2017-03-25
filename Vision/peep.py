#!/usr/bin/env python2

import cv2
import numpy as np
from nms import non_max_suppression_fast as non_max_suppression
import imutils

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
cap = cv2.VideoCapture(0)
cap.set(3, 1024)
cap.set(4, 720)

while (True):
    ret, image = cap.read()
    image = imutils.resize(image, width=min(400, image.shape[1]))
    orig = image.copy()

    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

    for (x, y, w, h) in rects:
        cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, overlapThresh=0.65)

    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

    cv2.imshow("output", image)
    ch = 0xFF & cv2.waitKey(1)
    if ch == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

