import time
import serial
#import aiming

try:
	ser = serial.Serial()
	ser.baudrate = 115600
	ser.port = 'COM3'
	ser.open()
except IOError as ioError:
	print ioError

def moveLeft(clientConnection, args):
	x = None
	
	if args[1] == None:
		return
	
	try:
		x = float(args[1])
	except ValueError:
		return
		
	if x < -1.0:
		x = -1.0
	elif x > 1.0:
		x = 1.0
	
	print "Moving Left " + str(x) + " " + time.strftime("%H:%M:%S", time.gmtime())
	try:
		ser.write(b"MoveLeft " + str(x) + "\n")
	except IOError:
		pass
	
def moveRight(clientConnection, args):
	x = None
	
	if args[1] == None:
		return
	
	try:
		x = float(args[1])
	except ValueError:
		return
		
	if x < -1.0:
		x = -1.0
	elif x > 1.0:
		x = 1.0
	
	print "Moving Right " + str(x) + " " + time.strftime("%H:%M:%S", time.gmtime())
	try:
		ser.write(b"MoveRight " + str(x) + "\n")
	except IOError:
		pass

def setMode(clientConnection, args):
	
	try:
		x = int(args)
	except ValueError:
		return
	
	print "Setting Mode " + str(x) + time.strftime("%H:%M:%S", time.gmtime())
	#call automatic aiming
	#aiming.setMode(args)
	
functions = {"MoveLeft":moveLeft, 
			"MoveRight":moveRight,
			"SetMode":setMode}

