thresh = 1
lineSize = 1
initialValue = 1
dropOff = 0
everyPixel = 1

#Key Input
delay = 200;
keyCode = cv2.waitKey(delay) 

if keyCode == 49: #1
	initialValue+=1

if keyCode == 50: #2
	initialValue-=1
	
if keyCode == 51: #3
	dropOff+=1

if keyCode == 52: #4
	dropOff-=1
	
if keyCode == 53: #5
	everyPixel+=1

if keyCode == 54: #6
	everyPixel-=1
	
#-----------------

if keyCode == 119: #w
	thresh+=0.1
	
if keyCode == 115: #s
	thresh-=0.1
	
if keyCode == 100: #a
	lineSize+=1
	
if keyCode == 97: #d
	lineSize-=1
	
#print values
os.system('cls')
print "initialValue: " + str(initialValue)
print "dropOff: " + str(dropOff)
print "everyPixel: " + str(everyPixel)
print "thresh: " + str(thresh)
print "lineSize: " + str(lineSize)

/*-----------------------------*/

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

/*------------------------------*/

#(targets, medics, robots) = filterer.filterTargets(grayscaleImage, (targets, medics, robots))

#just for testing
#border = targetfilterer.detectBorder(grayscaleImage)
#cv2.drawContours(borderImage, [border],-1,(0,0,255),2)

#linesImage = targetfilterer.hammLines(grayscaleImage, thresh = 0, lineSize = 1, lineLength = 200)
#linesImage = targetfilterer.houghLines(grayscaleImage)