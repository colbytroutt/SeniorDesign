import numpy
import cv2
import math
import os
from timeit import default_timer as timer

import t
import json
import targetdetection
import targetfilterer
import base64
import random

TARGET_COLOR_BGR = (0, 0, 255)
MEDIC_COLOR_BGR = (255, 0, 0)
ROBOT_COLOR_BGR = (0, 255, 0)

CAMERA_FOV = 70

def aimCamera(x, width):
	yaw = (-CAMERA_FOV/2) + ((x/width)*CAMERA_FOV)  
	#aimCameraOnArduino(yaw)
	prioritization.updateTurningMemory(yaw)
		
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
	
	t.startServer()
	
	#Camera feed
	cap = cv2.VideoCapture(0)
	
	#Image feed
	#image = cv2.imread('bigTest.png')

	fpsTimer = timer()
	count = 0
	targetAverageTime = 0
	medicAverageTime = 0
	
	#networked variables
	dartAmmo = 54
	ballAmmo = 3
	targetStatus = "OFF"
	
	random.seed(None)
	
	while(True):
	
		#Camera feed
		ret, image = cap.read()
		image = cv2.resize(image, (400, 300))
		grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		#Find Targets
		start = timer()
		targets = targetdetection.detectTargets(grayscaleImage)
		#targets = []
		end = timer()
		targetAverageTime+=(end-start)*1000
				
		#Find Medics
		start = timer()
		medics = targetdetection.detectMedics(grayscaleImage)
		#medics = []
		end = timer()
		medicAverageTime+=(end-start)*1000
		
		#Find Robots
		#robots = targetdetection.detectRobots(grayscaleImage)
		robots = []
		
		#(targets, medics, robots) = filterer.filterTargets(grayscaleImage, (targets, medics, robots))
		
		#just for testing
		borderImage = numpy.copy(image)
		#border = targetfilterer.detectBorder(grayscaleImage)
		#cv2.drawContours(borderImage, [border],-1,(0,0,255),2)
		
		#linesImage = targetfilterer.hammLines(grayscaleImage, thresh = 0, lineSize = 1, lineLength = 200)
		#linesImage = targetfilterer.houghLines(grayscaleImage)
		
		#Draw boundin boxes on targets
		borderImage = drawTargets(borderImage, (targets, medics, robots))
		
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
		
		dartAmmo = random.randint(0, 100)
		ballAmmo = random.randint(0, 100)

		ret, png = cv2.imencode('.png', borderImage)
		
		data = {}
		data["image"] = base64.b64encode(png)
		data["dartAmmo"] = dartAmmo
		data["ballAmmo"] = ballAmmo
		data["targetStatus"] = targetStatus
		
		data = json.dumps(data, separators=(',',':'))
		
		#show image
		t.broadCastMessage(data)
		#cv2.imshow('Detection', borderImage)
		#cv2.imshow('Capture', image)
		
		if(timer() - fpsTimer > 1):
			fpsTimer = timer()
			os.system('cls')
			print("TargetDetection: ")
			print(str(targetAverageTime/count) + " ms")
			print("MedicDetection: ")
			print(str(medicAverageTime/count) + " ms")
			print("FPS: ")
			print(count)
			
			#reset stuff
			targetAverageTime = 0
			medicAverageTime = 0
			count = 0
		else:
			count+=1
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
			
	cap.release()
	cv2.destroyAllWindows()