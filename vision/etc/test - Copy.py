import numpy
import test

targetMemory = []

def updateTurningMemory(yaw):

	rotationMatrix = [[cos(yaw) , 0, sin(yaw), 0],
					  [0        , 0, 0       , 0],
					  [-sin(yaw), 0, cos(yaw), 0],
					  [0        , 0, 0       , 1]]

	for i in range(len(targetMemory)):
		((x, y, z), count) = targetMemory[i]
		rotatedCoords = numpy.dot(numpy.array(rotationMatrix), numpy.array([x, y, z]))
		targetMemory[i] = ((rotatedCoords[0], rotatedCoords[1], rotatedCoords[2]), count)
	
def updateMovingMemory(xTranslation, yTranslation, zTranslation):

	translationMatrix = [[1, 0, 0, xTranslation],
						 [0, 1, 0, yTranslation],
						 [0, 0, 1, zTranslation],
						 [0, 0, 0, 1]]

	for i in range(len(targetMemory)):
		((x, y, z), count) = targetMemory[i]
		translatedCoords = numpy.dot(numpy.array(translationMatrix), numpy.array([x, y, z]))
		targetMemory[i] = ((translatedCoords[0], translatedCoords[1], translatedCoords[2]), count))


def priotize((targets, medics, robots)):
	refinedTargets = []
	
	wasInThere = False
	
	for (sx, sy, w, h) in targets:
		x = sx + w/2
		y = sy + h/2
		z = test.getDistance(x, y)
		
		for i  in range(len(targetMemory))
			((tmX, tmY), count) = targetMemory[i] 
			if tmX == x and tmY == y:
				wasInThere = True
				if count < 2:
					targetMemory[i] = ((x, y, z), count+1)
					refinedTargets.append((sx, sy, w, h))
		
		if wasInThere == False:
			targetMemory[i].append(((x, y, z), 0))
			refinedTargets.append(sx, sy, w, h)

	return refinedTargets

def drawTargets(image, (targets, medics, robots)):
	for (x,y,w,h) in targets:
		cv2.rectangle(image, (x,y), (x+w,y+h), TARGET_COLOR_BGR, 2)
	
	for (x,y,w,h) in medics:
		cv2.rectangle(image, (x,y), (x+w,y+h), MEDIC_COLOR_BGR, 2)
		
	for (x,y,w,h) in robots:
		cv2.rectangle(image, (x,y), (x+w,y+h), ROBOT_COLOR_BGR, 2)
	
	return image