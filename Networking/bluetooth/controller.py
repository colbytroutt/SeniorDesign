import PyCmdMessenger

arduino = PyCmdMessenger.ArduinoBoard("COM4",baud_rate=9600)

commands = [["aim","ii"],
            ["error","s"]]

# Initialize the messenger
messenger = PyCmdMessenger.CmdMessenger(arduino,commands)

def aim(pan, tilt):
	messenger.send("aim", pan, tilt)
	#msg = messenger.receive()

while(True):
	try:
		number=int(input('Input:'))
	except ValueError:
		print "Not a number"
	
	pan(number)
	