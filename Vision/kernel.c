#include <stdio.h>

__device__ void drawLineInDirection(int *image, int width, int height, int pointX, int pointY, float slope, int lineSize, int isVertical, int direction, int initialValue, int dropOff, int everyPixel) {

	//keeps track of real values on line
	float fX = (float)pointX;
	float fY = (float)pointY;
	
	//used for indexing
	int iX = pointX;
	int iY = pointY;

	int l;
	int thickX;
	int thickY;
	
	int increaseValue = initialValue;
	int count = everyPixel;

	int directionFactor = 1;
	if(direction != 0) {
		directionFactor = -1;
		
		//determines next point of line
		if(isVertical == 0) {
			//printf("NOT VERTICAL\\n");
			fY -= slope * directionFactor;
			fX += 1 * directionFactor;
			iX = (int)round(fX);
			iY = (int)round(fY);
		} else {
			//printf("VERTICAL\\n");
			fY -= 1 * directionFactor;
			iY = (int)round(fY);
		}
	}

	//printf("fX: %f\\n", fX);
	//printf("fY: %f\\n", fY);
	//printf("iX: %d\\n", iX);
	//printf("iY: %d\\n", iY);

	//draw until line is out of bounds
	while(iX >= 0 && iX < width && iY >= 0 && iY < height && increaseValue > 0) {
		
		//draws a thicker line
		for(l=-lineSize/2; l<=lineSize/2; l++) {
			
			//printf("l: %d\\n", l);
			
			if(fabsf(slope) > 1 || isVertical) {
				//printf("SLOPE HIGH\\n");
				thickX = iX + l;
				thickY = iY;
			} else {
				//printf("SLOPE LOW\\n");
				thickX = iX;
				thickY = iY + l;
			}
			
			//printf("thickX: %d\\n", thickX);
			//printf("thickY: %d\\n", thickY);
			
			if(thickX >= 0 && thickX < width && thickY >= 0 && thickY < height) {
				//printf("adding at: %d %d\\n", thickX, thickY);
				atomicAdd(&(image[thickY*width + thickX]), increaseValue);
			}
		}
		
		if(count > 20) {
			increaseValue -= dropOff;
			count = 0;
		}
		count++;
		
		//determines next point of line
		if(isVertical == 0) {
			//printf("NOT VERTICAL\\n");
			fY -= slope * directionFactor;
			fX += 1 * directionFactor;
			iX = (int)round(fX);
			iY = (int)round(fY);
		} else {
			//printf("VERTICAL\\n");
			fY -= 1 * directionFactor;
			iY = (int)round(fY);
		}
		
		//printf("fX: %f\\n", fX);
		//printf("fY: %f\\n", fY);
		//printf("iX: %d\\n", iX);
		//printf("iY: %d\\n", iY);
		
	}
	//printf("%d %d %d\\n", -1/2, (-1/2)+1, lineSize/2);

}

__device__ void drawLine(int *image, int width, int height, int pointX, int pointY, float slope, int lineSize, int isVertical, int initialValue, int dropOff, int everyPixel) {

	//draw line forward
	drawLineInDirection(image, width, height, pointX, pointY, slope, lineSize, isVertical, 0, initialValue, dropOff, everyPixel);
	//draw line backward
	drawLineInDirection(image, width, height, pointX, pointY, slope, lineSize, isVertical, 1, initialValue, dropOff, everyPixel);
}

__global__ void drawLines(int *newImage, float *hGradientImage, float *vGradientImage, int width, int height, float thresh, int lineSize, int initialValue, int dropOff, int everyPixel) {
	
	int idx = threadIdx.x + blockDim.x * blockIdx.x;
	int idy = threadIdx.y + blockDim.y * blockIdx.y;

	int i;
	float slope;
	
	//remove overflow threads
	if (idx >= width-1 || idy >= height-1) {
		return;
	}
	
	//1d index for gradient images
	i = idy*width + idx;
	
	//threshold low values in gradient input
	if(fabsf(hGradientImage[i]) < thresh) {
		hGradientImage[i] = .0;
	}

	if(fabsf(vGradientImage[i]) < thresh) {
		vGradientImage[i] = .0;
	}
	
	if(hGradientImage[i] == .0) {
		//undefined
		if (vGradientImage[i] == .0) {
			return;
		}
	
		//draw vertical line
		//printf("coords: %d %d\\n", idx, idy);
		//printf("i: %d\\n", i);
		drawLine(newImage, width, height, idx, idy, 0, lineSize, 1, initialValue, dropOff, everyPixel);
		return;
	}
	
	//printf("width: %d\\n", width);
	//printf("height: %d\\n", height);

	//draw line
	
	slope = vGradientImage[i]/hGradientImage[i];
	
	//printf("%f\n", slope); 
	drawLine(newImage, width, height, idx, idy, slope, lineSize, 0, initialValue, dropOff, everyPixel);

	//printf("%d %d: %d %d %f %f \\n", idx, idy, vGradientImage[i], hGradientImage[i], slope, round(3.8));
}