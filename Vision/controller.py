import PyCmdMessenger

arduino = PyCmdMessenger.ArduinoBoard("COM4",baud_rate=9600)

commands = [["aim","ii"],
			["t", "i"],
            ["error","s"]]

# Initialize the messenger
messenger = PyCmdMessenger.CmdMessenger(arduino,commands)

def aim(yaw, pitch):
	messenger.send("aim", int(-yaw), int(-pitch))

if __name__ == "__main__":
	while(True):
		try:
			number=int(input('Input:'))
		except ValueError:
			print "Not a number"
		
		aim(0, number)
	