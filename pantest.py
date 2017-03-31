import controller

if __name__ == "__main__":
	while(True):
		try:
			number=int(input('Input:'))
		except ValueError:
			print "Not a number"
		
		controller.aim(number, 0)
	