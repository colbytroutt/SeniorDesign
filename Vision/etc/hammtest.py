import targetfilterer
import time

def StressTest(): 
	
	start = timer()
	
	width = 1920
	height = 1080
	
	hGradientImage = numpy.random.rand(width, height).astype(numpy.float32)
	vGradientImage = numpy.random.rand(width, height).astype(numpy.float32)
	
	filteredImage = targetfilterer.hammLines(hGradientImage, vGradientImage, thresh = 1, lineSize = max(width, height), initialValue = 1, dropOff = 0, everyPixel = 1)
	
	end = timer()
	
	print "Time Elapsed:"
	print (end - start)
	
	print "Output Image:"
	print filteredImage
	
def SmallTest():

	hGradientImage = [[0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0.5,  0,  0],]
	
	vGradientImage = [[0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0,  0,  0],
					  [0.5,  0,  0]]
	
	
	hGradientImage = numpy.array(hGradientImage, dtype=numpy.dtype(numpy.float32))
	vGradientImage = numpy.array(vGradientImage, dtype=numpy.dtype(numpy.float32))
	
	filteredImage = targetfilterer.hammLines(hGradientImage, vGradientImage, thresh = 1, lineSize = max(width, height), initialValue = 1, dropOff = 0, everyPixel = 1)
	
	print "Output Image:"
	print filteredImage

if __name__ == "__main__":

	print "HAMM SMALL TEST:"
	smallTest()
	print "HAMM STRESS TEST"
	StressTest()