import cv2
import numpy

#Load classifiers
TARGET_CLASSIFIER = cv2.CascadeClassifier("HaarCascades/haarcascade_frontalface_default.xml")
TARGET_CLASSIFIER1 = cv2.CascadeClassifier("HaarCascades/haarcascade_profileface.xml")
MEDIC_CLASSIFIER = cv2.CascadeClassifier("HaarCascades/hogcascade_pedestrians.xml")

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detectTargets(grayscaleImage):
	return TARGET_CLASSIFIER.detectMultiScale(grayscaleImage, 1.3, 5)
	#targets2 = TARGET_CLASSIFIER1.detectMultiScale(grayscaleImage, 1.3, 5)
	"""
	if isinstance(targets1, tuple):
		return targets2
	if isinstance(targets2, tuple):
		return targets1
	
	return numpy.concatenate((targets1, targets2))
	"""
	
def detectMedics(grayscaleImage):
	"""
	weightedMedics = []

	(medics, weights) = hog.detectMultiScale(grayscaleImage, winStride=(4, 4), padding=(8, 8), scale=1.2)
	for i in range(len(weights)):
		if weights[i] >= 2.0:
			weightedMedics.append(medics[i])
			
	return weightedMedics
	"""
	return MEDIC_CLASSIFIER.detectMultiScale(grayscaleImage, 1.3, 5)
	
def detectRobots(grayscaleImage):
	return [] 