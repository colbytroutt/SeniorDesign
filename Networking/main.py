from server import *
import time

BLUETOOTH_NAME = "Blue Team Robot"
UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

server = Server(BLUETOOTH_NAME, UUID)
server.start()
print("Server Started")

while True:
	try:
		time.sleep(1)
	except KeyboardInterrupt:
		server.stop()
		break