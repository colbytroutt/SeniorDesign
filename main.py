import cv2
import math
import base64
import random
import time
import json
import threading
import numpy as np
from timeit import default_timer as timer

import config
if config.ARDUINO_CONNECTED: import hardware.hardwarecontroller as hc
from networking import webserver as ws
from vision import targetdetection
from vision import prioritization

targetMode = config.TARGET_MODE_DEFAULT
medicMode = config.MEDIC_MODE_DEFAULT
robotMode = config.ROBOT_MODE_DEFAULT
parallelMode = config.PARALLEL_MODE

displayMode = config.DISPLAY_MODE

flywheelMode = config.FLYWHEEL_MODE_DEFAULT
fireMode = config.FIRE_MODE_DEFAULT
aimMode = config.AIM_MODE_DEFAULT

def fire():
	if config.ARDUINO_CONNECTED:
		if fireMode:
			hc.fire()
	time.sleep(0)

def aim(x, y, imageWidth, imageHeight):

	cameraFOV = config.CAMERA_FOV
	delayPerAngle = config.DELAY_PER_ANGLE

	yaw = (x - (imageWidth/2))*(float(CAMERA_FOV)/imageWidth)
	pitch = (y - (imageHeight/2))*(float(CAMERA_FOV)/imageHeight)

	if abs(yaw) < 2:
		yaw = 0

	if abs(pitch) < 2:
		pitch = 0

	if config.ARDUINO_CONNECTED:
		if aimMode:
			hc.aim(yaw, pitch)
		
	time.sleep(DELAY_PER_ANGLE*max(abs(yaw), abs(pitch)))
	#prioritization.updateTurningMemory(yaw)

def foo(x, y, imageWidth, imageHeight, aimMode, fireMode):
	if aimMode is True:
			aim(x, y, imageWidth, imageHeight)
	if fireMode is True:
			fire()

def getDistance(x, y):
	return 0

def drawTargets(image, (targets, medics, robots)):

	for (x,y,w,h) in targets:
		cv2.rectangle(image, (x,y), (x+w,y+h), config.TARGET_COLOR_BGR, 2)

	for (x,y,w,h) in medics:
		cv2.rectangle(image, (x,y), (x+w,y+h), config.MEDIC_COLOR_BGR, 2)

	for (x,y,w,h) in robots:
		cv2.rectangle(image, (x,y), (x+w,y+h), config.ROBOT_COLOR_BGR, 2)

	return image

def sendVideoToServer(image):
	
	resizedImage = np.copy(image);
	
	resizedImage = cv2.resize(resizedImage, (300, 400))

	ret, png = cv2.imencode('.png', image)

	data = {}
	data["image"] = base64.b64encode(png)
	data["dartAmmo"] = dartAmmo
	data["ballAmmo"] = ballAmmo
	data["targetStatus"] = targetStatus

	data = json.dumps(data, separators=(',',':'))

	ws.broadCastMessage(data)
	
if __name__ == "__main__":

	#Camera feed
	cap = cv2.VideoCapture(0)

	cap.set(3, 1024);
	cap.set(4, 720);

	#Image feed
	#image = cv2.imread('SampleImages/picture.jpg')

	fpsTimer = timer()
	fpsCount = 0
	
	targetAverageTime = 0
	medicAverageTime = 0
	robotAverageTime = 0
	parallelAverageTime = 0

	#networked variables
	dartAmmo = 20
	ballAmmo = 25
	targetStatus = "ON"

	random.seed(None)

	ws.startServer()
	
	if robotMode is True:
		targetdetection.initializeRobot()
	
	if parallelMode is True:
		targetdetection.initParallelization()

	t = None

	while(True):

		#Camera feed
		ret, image = cap.read()
		grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		targets = np.array([])
		medics = np.array([])
		robots = np.array([])
		
		#find targets sequentially
		if parallelMode is False:
		
			#Find Targets
			start = timer()
			if targetMode is True:
				targets = targetdetection.detectTargets(grayscaleImage)
			end = timer()
			targetAverageTime+=(end-start)*1000

			#Find Medics
			start = timer()
			if medicMode is True:
				medics = targetdetection.detectMedics(grayscaleImage)
			end = timer()
			medicAverageTime+=(end-start)*1000

			#Find Robots
			start = timer()
			if robotMode is True:
				robots = targetdetection.detectRobots(image)
			end = timer()
			robotAverageTime+=(end-start)*1000
		
		else:
			start = timer()
			(targets, medics, robots) = targetdetection.detectAllTargetsParallel(grayscaleImage)
			end = timer()
			parallelAverageTime+=(end-start)*1000


		#Draw bounding boxes on targets
		image = drawTargets(image, (targets, medics, robots))
		
		if displayMode is True:
			cv2.imshow('Video Client', image)

		targetToFire = prioritization.prioritize((targets, medics, robots))
		if targetToFire != None:
			(x, y, width, height) = targetToFire
			if (t == None) or not t.isAlive():
				t = threading.Thread(target = foo, args = (x+(width/2), y+(height/2), grayscaleImage.shape[1], grayscaleImage.shape[0], aimMode, fireMode))
				t.start()

		
		sendVideoToServer(image)

		if(timer() - fpsTimer > 1):
			fpsTimer = timer()

			if(fpsCount != 0):
				if parallelMode is False:
					print("Target Detection: " + str(targetAverageTime/fpsCount) + " ms")
					print("Medic Detection: " + str(medicAverageTime/fpsCount) + " ms")
					print("Robot Detection: " + str(robotAverageTime/fpsCount) + " ms")
				else:
					print("Parallel Detection: " + str(parallelAverageTime/fpsCount) + " ms")

			print("FPS: " + str(fpsCount))
			print("Target Mode: {}\tMedic Mode: {}\tRobot Mode: {}\tDisplay Mode: {}".format(targetMode, medicMode, robotMode, displayMode))
			print("Flywheel Mode: {}\tAim Mode: {}\tFire Mode: {}".format(flywheelMode, aimMode, fireMode))
			
			#reset stuff
			targetAverageTime = 0
			medicAverageTime = 0
			robotAverageTime = 0
			fpsCount = 0
		else:
			fpsCount+=1

		ch = cv2.waitKey(1) & 0xFF

		if ch == ord('q'):
				break
		elif ch == ord('1'):
			targetMode = not targetMode
		elif ch == ord('2'):
			targetMode = not medicMode
		elif ch == ord('3'):
			robotMode = not robotMode
		elif ch == ord ('4'):
			displayMode = not displayMode
			cv2.destroyAllWindows()
		elif ch == ord ('5'):
			if flywheelMode is true:
				hc.halt()
			else:
				hc.start()
				flywheelMode = not flywheelMode
		elif ch == ord('a'):
			aimMode = not aimMode
		elif ch == ord('f'):
			fireMode = not fireMode

	if parallelMode is True:
		targetdetection.destroyThreads()
	
	if config.ARDUINO_CONNECTED is True:
		hc.halt()
		
	cap.release()
	cv2.destroyAllWindows()
