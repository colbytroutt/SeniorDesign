import numpy
import cv2
import math
import os

import targetdetection
import targetfilterer

TARGET_COLOR_BGR = (0, 0, 255)
MEDIC_COLOR_BGR = (255, 0, 0)
ROBOT_COLOR_BGR = (0, 255, 0)

def drawTargets(image, (targets, medics, robots)):
	for (x,y,w,h) in targets:
		cv2.rectangle(image, (x,y), (x+w,y+h), TARGET_COLOR_BGR, 2)
	
	for (x,y,w,h) in medics:
		cv2.rectangle(image, (x,y), (x+w,y+h), MEDIC_COLOR_BGR, 2)
		
	for (x,y,w,h) in robots:
		cv2.rectangle(image, (x,y), (x+w,y+h), ROBOT_COLOR_BGR, 2)
	
	return image
	
if __name__ == "__main__":
	
	#Camera feed
	cap = cv2.VideoCapture(0)
	
	#Image feed
	#image = cv2.imread('bigTest.png')

	while(True):
		#Camera feed
		ret, image = cap.read()
		grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		#Find Targets
		targets = targetdetection.detectTargets(grayscaleImage)
		#targets = []
		#Find Medics
		#medics = targetdetection.detectMedics(grayscaleImage)
		medics = []
		#Find Robots
		#robots = targetdetection.detectRobots(grayscaleImage)
		robots = []
		
		#(targets, medics, robots) = filterer.filterTargets(grayscaleImage, (targets, medics, robots))
		
		#just for testing
		borderImage = numpy.copy(image)
		border = targetfilterer.detectBorder(grayscaleImage)
		cv2.drawContours(borderImage, [border],-1,(0,0,255),2)
		
		linesImage = targetfilterer.hammLines(grayscaleImage, thresh = 5.1, lineSize = 1, initialValue = 10, dropOff = 6, everyPixel = 5)
		#linesImage = targetfilterer.houghLines(grayscaleImage)
		
		#Draw boundin boxes on targets
		borderImage = drawTargets(borderImage, (targets, medics, robots))
		
		#show image
		cv2.imshow('Detection', linesImage)
		cv2.imshow('Capture', borderImage)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()