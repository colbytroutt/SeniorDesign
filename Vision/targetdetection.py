import cv2
import numpy
import threading
from multiprocessing import Process, Queue, Lock
import multiprocessing

#Load classifiers
TARGET_CLASSIFIER = cv2.CascadeClassifier("HaarCascades/haarcascade_frontalface_default.xml")
TARGET_CLASSIFIER1 = cv2.CascadeClassifier("HaarCascades/haarcascade_profileface.xml")
MEDIC_CLASSIFIER = cv2.CascadeClassifier("HaarCascades/hogcascade_pedestrians.xml")

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

pool = None

def detectTargets(grayscaleImage):

	targets = TARGET_CLASSIFIER.detectMultiScale(grayscaleImage, None, None, scaleFactor=1.3, minNeighbors =5, flags=0, minSize =(50, 50))
	
	if isinstance(targets, tuple):
		targets = numpy.array([])
	
	return targets
	
def detectMedics(grayscaleImage):
	
	#medics = MEDIC_CLASSIFIER.detectMultiScale(grayscaleImage, None, None, scaleFactor=1.3, minNeighbors =5, flags=0, minSize =(50, 50))
	medics = numpy.array([])
	
	if isinstance(medics, tuple):
		medics = numpy.array([])
		
	return medics
	
def detectRobots(grayscaleImage):
	
	robots = numpy.array([])

	return robots
	
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