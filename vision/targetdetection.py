import cv2
import numpy as np
import threading
from multiprocessing import Process, Queue, Lock
import multiprocessing
#import robot
from nms import non_max_suppression_fast
import sys, os

#Load classifiers
TARGET_CLASSIFIER = cv2.CascadeClassifier(os.path.dirname(os.path.abspath(__file__)) + "/" + "haarcascades/haarcascade_frontalface_default.xml")
TARGET_CLASSIFIER1 = cv2.CascadeClassifier(os.path.dirname(os.path.abspath(__file__)) + "/" + "haarcascades/haarcascade_profileface.xml")
MEDIC_CLASSIFIER = cv2.CascadeClassifier(os.path.dirname(os.path.abspath(__file__)) + "/" + "haarcascades/haarcascade_lowerbody.xml")

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

pool = None
robotDetect = None
fgbg = None

def initializeRobot():
	#global robotDetect
	#robotDetect = robot.Robot()
	global fgbg
	fgbg = cv2.createBackgroundSubtractorMOG2(history = 500, varThreshold = 16, detectShadows = False)

def detectTargets(grayscaleImage):

        targets = TARGET_CLASSIFIER.detectMultiScale(grayscaleImage, scaleFactor=1.3, minNeighbors =5, flags=0)

	if isinstance(targets, tuple):
	    targets = np.array([])

	return targets

def detectMedics(grayscaleImage):

        """
	medics, weights = hog.detectMultiScale(grayscaleImage, winStride=(4, 4), padding=(8,8), scale=1.05)
	medics = np.array([[x, y, x + w, y + h] for (x, y, w, h) in medics])
	medics = non_max_suppression_fast(medics, overlapThresh=0.65)
        """
        medics = MEDIC_CLASSIFIER.detectMultiScale(grayscaleImage, scaleFactor=1.3, minNeighbors=5, flags=0)

	if isinstance(medics, tuple):
		medics = np.array([])

	return medics

def detectRobots(colorImage):
	global fgbg

	fgmask = fgbg.apply(colorImage, learningRate = 1.0/1)
	kernel = np.ones((30,30), np.uint8)
	erosion = cv2.erode(fgmask, kernel, iterations = 1)
#	dilation = cv2.dilate(fgmask, kernel, iterations = 1)

	contourImage, contours, hierarchy = cv2.findContours(fgmask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	biggestContour = None
	biggestContourArea = 0
	for contour in contours:
		area = cv2.contourArea(contour)
		if area > biggestContourArea and area > 50:
			peri = cv2.arcLength(contour, True)
			approx = cv2.approxPolyDP(contour, 0.01*peri, True)
			biggestContour = approx
			biggestContourArea = area

	if biggestContour is not None:
		return np.array([cv2.boundingRect(biggestContour)])

	return np.array([])

	#return robotDetect.classify(colorImage)

def initParallelization():
	global pool
	pool = multiprocessing.Pool(3)

def detectAllTargetsParallel(grayscaleImage):
	global pool
	targetWorker = pool.apply_async(detectTargets, args=(grayscaleImage, ))
	medicWorker = pool.apply_async(detectMedics, args=(grayscaleImage, ))
	robotWorker = pool.apply_async(detectRobots, args=(grayscaleImage, ))

	targets = targetWorker.get()
	medics = medicWorker.get()
	robots = robotWorker.get()
	return (targets, medics, robots)

def destroyThreads():
	pool.close()
	pool.join()
