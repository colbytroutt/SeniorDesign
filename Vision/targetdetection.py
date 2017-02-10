import cv2

#Load classifiers
TARGET_CLASSIFIER = cv2.CascadeClassifier('HaarCascades/haarcascade_frontalface_default.xml')
MEDIC_CLASSIFIER = cv2.CascadeClassifier('HaarCascades/haarcascade_fullbody.xml')

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detectTargets(grayscaleImage):
	return TARGET_CLASSIFIER.detectMultiScale(grayscaleImage, 1.3, 5)
	
def detectMedics(grayscaleImage):
	(medics, weights) = hog.detectMultiScale(grayscaleImage, winStride=(4, 4), padding=(8, 8), scale=1.2)
	return medics

def detectRobots(grayscaleImage):
	return [] 