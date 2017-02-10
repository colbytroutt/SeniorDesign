import pycuda.driver as drv
import pycuda.tools
import pycuda.autoinit
import numpy
from pycuda.compiler import SourceModule
from timeit import default_timer as timer
import cv2
import math

BLOCK_SIZE = (32, 32)

#Compile hammLines kernel
kernelFile = open('kernel.c', 'r')
mod = SourceModule(kernelFile.read())

def filterTargets(grayscaleImage, (targets, medics, robots)):
	
	#detectBorder()
	
	#use points to find overlap with targets
	
	return (targets, medics, robots)
	
def detectBorder(grayscaleImage):
	
	linesImage = hammLines(grayscaleImage, thresh = 5.1, lineSize = 1, initialValue = 10, dropOff = 6, everyPixel = 5)
	#linesImage = houghLines(grayscaleImage)
	
	image, contours, hierarchy = cv2.findContours(numpy.copy(linesImage), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
	biggestContour = None
	biggestContourArea = 0
	for contour in contours:
		area = cv2.contourArea(contour)
		if area > biggestContourArea and area > 2000:
			peri = cv2.arcLength(contour, True)
			approx = cv2.approxPolyDP(contour, 0.01*peri, True)
			if len(approx) == 4:
				biggestContour = approx
				biggestContourArea = area

	#rotRect = cv2.minAreaRect(biggestContour)
	#box = cv2.boxPoints(rotRect)
	#box = numpy.int0(box)
	
	return biggestContour
	
#TODO: FIX MAGIC NUMBERS
def houghLines(grayscaleImage):

	edges = cv2.Canny(grayscaleImage, 66, 133, apertureSize=3)
	
	borderImage = numpy.zeros_like(grayscaleImage)
	
	lines = cv2.HoughLines(edges,1,numpy.pi/180, 100)
	if lines != None:
		N = lines.shape[0]
		for i in range(N):
			rho,theta = lines[i][0]
			a = numpy.cos(theta)
			b = numpy.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))
			cv2.line(borderImage,(x1,y1),(x2,y2),255,2)
	
	"""
	lines = cv2.HoughLinesP(edges, 1, numpy.pi/180, 50, None, 1, 50)

	N = lines.shape[0]
	for i in range(N):
		x1 = lines[i][0][0]
		y1 = lines[i][0][1]    
		x2 = lines[i][0][2]
		y2 = lines[i][0][3]    
		cv2.line(borderImage,(x1,y1),(x2,y2),(255,0,0),2)
	"""
	
	return borderImage
	
#TODO: FIX MAGIC NUMBERS
def hammLines(grayscaleImage, thresh, lineSize, initialValue, dropOff, everyPixel):
	
	#create kernels using gaussian derivatives
	sigma = 3
	horizontalKernel = numpy.empty([sigma*3, sigma*3]).astype(numpy.float32)
	verticalKernel = numpy.empty([sigma*3, sigma*3]).astype(numpy.float32)
	for i in range(sigma*3):
		for j in range(sigma*3):	
			xx = j - (sigma*3/2) 
			yy = i - (sigma*3/2) 
			
			x = -xx * math.exp((-1/2) * (xx*xx + yy*yy) / (sigma*sigma))
			y = -yy * math.exp((-1/2) * (xx*xx + yy*yy) / (sigma*sigma))
			horizontalKernel[i][j] = y
			verticalKernel[i][j] = x
	
	#convolute kernels with input image
	horizontalImage = cv2.filter2D(grayscaleImage, cv2.CV_32F, horizontalKernel) / (horizontalKernel.shape[0]*horizontalKernel.shape[1])
	verticalImage = cv2.filter2D(grayscaleImage, cv2.CV_32F, verticalKernel) / (verticalKernel.shape[0]*verticalKernel.shape[1])

	drawLines = mod.get_function("drawLines")
	
	filteredImage = numpy.zeros_like(horizontalImage).astype(numpy.int32)
	
	dx, mx = divmod(horizontalImage.shape[1], BLOCK_SIZE[0])
	dy, my = divmod(horizontalImage.shape[0], BLOCK_SIZE[1])
	
	gridSize = (dx, dy)
	
	drawLines(drv.Out(filteredImage),
		drv.In(horizontalImage),
		drv.In(verticalImage),
		numpy.int32(horizontalImage.shape[1]),
		numpy.int32(horizontalImage.shape[0]),
		numpy.float32(thresh),
		numpy.int32(lineSize),
		numpy.int32(initialValue),
		numpy.int32(dropOff),
		numpy.int32(everyPixel),
		grid=(gridSize[0] + (mx>0), gridSize[1] + (my>0)),
		block=(BLOCK_SIZE[0], BLOCK_SIZE[1], 1))
	
	cv2.normalize(filteredImage, filteredImage, 0, 255, cv2.NORM_MINMAX)
	
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(filteredImage)
	thresh = 25
	low_values_indices = filteredImage < (thresh)  # Where values are low
	##print filteredImage
	high_values_indices = filteredImage >= (thresh)  # Where values are low
	filteredImage[low_values_indices] = 0  # All low values set to 0
	filteredImage[high_values_indices] = 255  # All low values set to 0
	
	#filteredImage = (filteredImage / maxVal) * 255
	#print maxVal
	
	return cv2.Canny(filteredImage.astype(numpy.uint8), 50, 50, apertureSize=3)