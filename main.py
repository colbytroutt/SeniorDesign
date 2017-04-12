#!/usr/bin/env python2
import cv2
import math
import base64
import random
import time
import json
import threading
import numpy as np
from timeit import default_timer as timer
import PyCmdMessenger

import config
import hardware.hardwarecontroller as hc
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

#networked variables
dartAmmo = 8
ballAmmo = 16

def fire():
        global ballAmmo
        global dartAmmo
        if config.TURRET_ARDUINO_CONNECTED:
            if fireMode:
                if ballAmmo > 0:
		    hc.fireBall()
                    ballAmmo -= 1
                    if ballAmmo == 0:
                        hc.setBallFlywheel(False)
                        hc.setDartFlywheel(True)
                else:
                    hc.fireDart()
                    dartAmmo -= 1
        time.sleep(config.FIRE_DELAY)

def aim(x, y, imageWidth, imageHeight):

	cameraFOV = config.CAMERA_FOV
	delayPerAngle = config.DELAY_PER_ANGLE

	yaw = (x - (imageWidth/2))*(float(cameraFOV)/imageWidth)
        #yaw -= 2
	pitch = (y - (imageHeight/2))*(float(cameraFOV)/imageHeight)
        pitch -= 5

	if abs(yaw) < 2:
		yaw = 0

	if abs(pitch) < 2:
		pitch = 0

        if not (yaw == 0 and pitch == 0):
	    if config.TURRET_ARDUINO_CONNECTED:
		if aimMode:
                        print "yaw: "
                        print yaw
                        print "\n"
                        print "pitch: "
                        print pitch
                        print "\n"
			hc.aim(yaw, pitch)

	time.sleep(delayPerAngle*max(abs(yaw), abs(pitch)))
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

	global targetMode
	global medicMode
	global robotMode

	global dartAmmo
	global ballAmmo

	if targetMode:
		targetStatus = "ON"
	else:
		targetStatus = "OFF"

	if medicMode:
		medicStatus = "ON"
	else:
		medicStatus = "OFF"

	if robotMode:
		robotStatus = "ON"
	else:
		robotStatus = "OFF"

	resizedImage = np.copy(image);

	resizedImage = cv2.resize(resizedImage, (480, 640))

	ret, jpg = cv2.imencode('.jpg', resizedImage)

	data = {}
	data["image"] = base64.b64encode(jpg)
	data["dartAmmo"] = dartAmmo
	data["ballAmmo"] = ballAmmo
	data["targetStatus"] = targetStatus
	data["medicStatus"] = medicStatus
	data["robotStatus"] = robotStatus

	data = json.dumps(data, separators=(',',':'))

	ws.broadCastMessage(data)

def motorReading():

	commands = [["setTargetMode", "i"],
				["setMedicMode", "i"],
				["setRobotMode", "i"],
				["setFiringMode", "i"],
				["error","s"]]

	arduino = PyCmdMessenger.ArduinoBoard(config.DRIVETRAIN_ARDUINO_NAME, baud_rate=9600)
	messenger = PyCmdMessenger.CmdMessenger(arduino, commands)

	global targetMode
	global medicMode
	global robotMode
	global flywheelMode
	global fireMode
        global ballAmmo

	while(True):
            try:
                msg = messenger.receive()

                if not isinstance(msg, tuple):
			continue

                print msg

		if msg[0] == "setTargetMode":
		    if msg[1][0]:
                        targetMode = True
                    else:
                        targetMode = False
		elif msg[0] == "setMedicMode":
		    if msg[1][0]:
                        medicMode = True
                    else:
                        medicMode = False
		elif msg[0] == "setRobotMode":
		    if msg[1][0]:
                        robotMode = True
                    else:
                        robotMode = False
		elif msg[0] == "setFiringMode":
                    if msg[1][0]:
                        flywheelMode = True
                        fireMode = True
                        if ballAmmo > 0:
			    hc.setBallFlywheel(True)
                        else:
                            hc.setDartFlywheel(True)
		    else:
                        flywheelMode = False
                        fireMode = False
                        if ballAmmo > 0:
			    hc.setBallFlywheel(False)
                        else:
                            hc.setDartFlywheel(False)
            except:
                pass

if __name__ == "__main__":

	#Camera feed
	cap = cv2.VideoCapture(0)

	cap.set(3, 1024)
	cap.set(4, 720)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, config.BRIGHTNESS) # Brightness
        cap.set(cv2.CAP_PROP_CONTRAST, config.CONTRAST) # Contrast
        cap.set(cv2.CAP_PROP_SATURATION, config.SATURATION) # Saturation
        cap.set(cv2.CAP_PROP_HUE, config.HUE) # Hue
        cap.set(cv2.CAP_PROP_GAIN, config.GAIN) # Gain
        #cap.set(15, 15) # Saturation

	#Image feed
	#image = cv2.imread('SampleImages/picture.jpg')

	fpsTimer = timer()
	fpsCount = 0

	targetAverageTime = 0
	medicAverageTime = 0
	robotAverageTime = 0
	parallelAverageTime = 0
        noTargetCounter = 0

	random.seed(None)

	ws.startServer()

	targetdetection.initializeRobot()

	if parallelMode is True:
		targetdetection.initParallelization()

	t = None

	if config.TURRET_ARDUINO_CONNECTED:
		hc.connect(config.TURRET_ARDUINO_NAME)
                hc.setBallDelay(115)
                hc.setDartDelay(200)

        if config.DRIVETRAIN_ARDUINO_CONNECTED:
	        motorThreading = None
 	        motorThreading = threading.Thread(target = motorReading)
	        motorThreading.daemon = True
	        motorThreading.start()

        if flywheelMode is True:
            hc.setBallFlywheel(True)

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
                                t.daemon = True
				t.start()

                if not (robotMode or targetMode or medicMode):
                    hc.resetAim()


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
			fpsCount += 1

                if len(robots) != 0 and len(medics) == 0:
                    time.sleep(2)

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
		        if config.TURRET_ARDUINO_CONNECTED:
                                if flywheelMode is True:
				        hc.setBallFlywheel(False)
                                        hc.setDartFlywheel(False)
			        else:
				        hc.setBallFlywheel(True)
                                        hc.setDartFlywheel(True)
		        flywheelMode = not flywheelMode
		elif ch == ord('a'):
			aimMode = not aimMode
		elif ch == ord('f'):
			fireMode = not fireMode

	if parallelMode is True:
		targetdetection.destroyThreads()

	if config.TURRET_ARDUINO_CONNECTED is True:
		hc.setBallFlywheel(False)
                hc.setDartFlywheel(False)

	cap.release()
	cv2.destroyAllWindows()
