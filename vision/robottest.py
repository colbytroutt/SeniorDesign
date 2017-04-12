import cv2
import numpy as np

if __name__ == "__main__":

	#Camera feed
	cap = cv2.VideoCapture(0)

	cap.set(3, 1024)
	cap.set(4, 720)
      
	fgbg = cv2.createBackgroundSubtractorMOG2(history = 0, varThreshold = 1000, detectShadows = False)

	while(True):

		#Camera feed
		ret, image = cap.read()
		grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		fgmask = fgbg.apply(image, learningRate = .01)

		contourImage, contours, hierarchy = cv2.findContours(fgmask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		biggestContour = None
		biggestContourArea = 0
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > biggestContourArea and area > 50:
				peri = cv2.arcLength(contour, True)
				approx = cv2.approxPolyDP(contour, 0.01*peri, True)
				biggestContour = approx
				biggestContourArea = area

	if biggestContour is not None:
		return np.array([cv2.boundingRect(biggestContour)])

		cv2.imshow("Image", fgmask)

		ch = cv2.waitKey(1) & 0xFF

		if ch == ord('q'):
		    	break

cap.release()
cv2.destroyAllWindows()


