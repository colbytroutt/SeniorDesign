import numpy
import cv2
import math
import os
from timeit import default_timer as timer

import vc
import json
import targetdetection
import prioritization
import base64
import random
import threading
import time
import hardwarecontroller as hc

TARGET_COLOR_BGR = (0, 0, 255)
MEDIC_COLOR_BGR = (255, 0, 0)
ROBOT_COLOR_BGR = (0, 255, 0)

CAMERA_FOV = 30

DELAY_PER_ANGLE = .2


def fire():
	hc.fire()
	time.sleep(0)

def aim(x, y, imageWidth, imageHeight):

	global CAMERA_FOV
	global DELAY_PER_ANGLE

	yaw = (x - (imageWidth/2))*(float(CAMERA_FOV)/imageWidth)
	pitch = (y - (imageHeight/2))*(float(CAMERA_FOV)/imageHeight)

	if abs(yaw) < 2:
		yaw = 0

	if abs(pitch) < 2:
		pitch = 0

	hc.aim(yaw, pitch)
	time.sleep(DELAY_PER_ANGLE*max(abs(yaw), abs(pitch)))
	#prioritization.updateTurningMemory(yaw)


def foo(x, y, imageWidth, imageHeight):
	aim(x, y, imageWidth, imageHeight)
	fire()


def getDistance(x, y):
	return 0

def drawTargets(image, (targets, medics, robots)):
	for (x,y,w,h) in targets:
		cv2.rectangle(image, (x,y), (x+w,y+h), TARGET_COLOR_BGR, 2)

	for (x,y,w,h) in medics:
		cv2.rectangle(image, (x,y), (x+w,y+h), MEDIC_COLOR_BGR, 2)

	for (x,y,w,h) in robots:
		cv2.rectangle(image, (x,y), (x+w,y+h), ROBOT_COLOR_BGR, 2)

	return image

if __name__ == "__main__":

	vc.startServer()
        targetdetection.initializeRobot()

	#Camera feed
	cap = cv2.VideoCapture(0)

	cap.set(3, 1024);
	cap.set(4, 720);
	cap.set(cv2.cv.CV_CAP_PROP_FPS, 30)
	print cap.get(cv2.cv.CV_CAP_PROP_FPS)

	#Image feed
	#image = cv2.imread('bigTest.png')

	fpsTimer = timer()
	fpsCount = 0
	targetAverageTime = 0
	medicAverageTime = 0

	#networked variables
	dartAmmo = 20
	ballAmmo = 25
	targetStatus = "OFF"

	random.seed(None)

	#targetdetection.initParallelization()

	t = None

	while(True):

		#Camera feed
		ret, image = cap.read()
		grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		#Find Targets

		start = timer()
		targets = targetdetection.detectTargets(grayscaleImage)
		end = timer()
		targetAverageTime+=(end-start)*1000

		#Find Medics
		start = timer()
		medics = targetdetection.detectMedics(grayscaleImage)
		end = timer()
		medicAverageTime+=(end-start)*1000

		#Find Robots
		robots = targetdetection.detectRobots(image)


		"""
		start = timer()
		(targets, medics, robots) = targetdetection.detectAllTargetsParallel(grayscaleImage)
		end = timer()
		targetAverageTime+=(end-start)*1000
		"""

		#targets = numpy.array([])
		#medics = numpy.array([])
		#robots = numpy.array([])

		#(targets, medics, robots) = filterer.filterTargets(grayscaleImage, (targets, medics, robots))

		#just for testing
		#border = targetfilterer.detectBorder(grayscaleImage)
		#cv2.drawContours(borderImage, [border],-1,(0,0,255),2)

		#linesImage = targetfilterer.hammLines(grayscaleImage, thresh = 0, lineSize = 1, lineLength = 200)
		#linesImage = targetfilterer.houghLines(grayscaleImage)

		#Draw boundin boxes on targets
		image = drawTargets(image, (targets, medics, robots))

		#test
		"""
		cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(image, numpy.array([0, 0, 0]), numpy.array([179, 255, 50]))

		kernel = numpy.ones((10,10), numpy.uint8)

		mask = cv2.erode(mask, kernel, iterations=1)
		mask = cv2.dilate(mask, kernel, iterations=1)

		edges = cv2.Canny(mask, 66, 133, apertureSize=3)
		image, contours, hierarchy = cv2.findContours(numpy.copy(edges), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		biggestContour = None
		biggestContourArea = 0
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > biggestContourArea and area > 0:
				peri = cv2.arcLength(contour, True)
				approx = cv2.approxPolyDP(contour, 0.000001*peri, True)
				#if len(approx) == 4:
				biggestContour = approx
				biggestContourArea = area

		cv2.drawContours(borderImage, [biggestContour],-1,(0,255,0),2)
		"""

		targetToFire = prioritization.priotize((targets, medics, robots))
		if targetToFire != None:
			(x, y, width, height) = targetToFire
			if (t == None) or not t.isAlive():
				t = threading.Thread(target = foo, args = (x+(width/2), y+(height/2), grayscaleImage.shape[1], grayscaleImage.shape[0]))
				t.start()

		#cv2.imshow('Capture', image)


		image = cv2.resize(image, (300, 400))

		ret, png = cv2.imencode('.png', image)

		data = {}
		data["image"] = base64.b64encode(png)
		data["dartAmmo"] = dartAmmo
		data["ballAmmo"] = ballAmmo
		data["targetStatus"] = targetStatus

		data = json.dumps(data, separators=(',',':'))

		vc.broadCastMessage(data)

		if(timer() - fpsTimer > 1):
			fpsTimer = timer()
			os.system('clear')

			if(fpsCount != 0):
				print("TargetDetection: ")
				print(str(targetAverageTime/fpsCount) + " ms")
				print("MedicDetection: ")
				print(str(medicAverageTime/fpsCount) + " ms")

			print("FPS: ")
			print(fpsCount)

			#reset stuff
			targetAverageTime = 0
			medicAverageTime = 0
			fpsCount = 0
		else:
			fpsCount+=1

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
        hc.halt()
