import PyCmdMessenger

commands = [["aim","ii"],
			["fireDart", " "], ["fireBall", " "],
			["setDartFlywheel", "?"], ["setBallFlywheel", "?"],
                        ["setDartDelay", "i"], ["setBallDelay", "i"],
                        ["error","s"]]

def connect():
	global messenger

	arduino = PyCmdMessenger.ArduinoBoard("/dev/ttyACM1", baud_rate=9600)
	messenger = PyCmdMessenger.CmdMessenger(arduino, commands)

def aim(yaw, pitch):
	global messenger
	messenger.send("aim", int(-yaw), int(-pitch))

def fireDart():
	global messenger
	messenger.send("fireDart")

def fireBall():
        global messenger
        messenger.send("fireBall")

def setDartFlywheel(cond):
	global messenger
	messenger.send("setDartFlywheel", cond)

def setBallFlywheel(cond):
	global messenger
	messenger.send("setBallFlywheel", cond)

def setDartDelay(delay):
        global messenger
        messenger.send("setDartDelay", delay)

def setBallDelay(delay):
        global messenger
        messenger.send("setBallDelay", delay)

if __name__ == "__main__":

	while(True):
		try:
			number=int(input('Input:'))
		except ValueError:
			print "Not a number"

		aim(number, 0)


