import PyCmdMessenger

commands = [["aim","ii"],
			["fire", " "],
			["error","s"]]

arduino = PyCmdMessenger.ArduinoBoard("COM4", baud_rate=9600)

messenger = PyCmdMessenger.CmdMessenger(arduino, commands)			
			
def init():
	
	return (messenger, arduino)
		
def aim(yaw, pitch):
	global messenger
	messenger.send("aim", int(-yaw), int(-pitch))
	
def fire():
	global messenger
	messenger.send("fire")

if __name__ == "__main__":

	while(True):
		try:
			number=int(input('Input:'))
		except ValueError:
			print "Not a number"
		
		aim(number, 0)
		
	