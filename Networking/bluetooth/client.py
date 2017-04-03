from bluetooth import *
import sys

uuid = "00001812-0000-1000-8000-00805f9b34fb"
target_name = "Xbox Wireless Controller"
target_address = None #"C8:3F:26:BD:D6:59"

nearby_devices = discover_devices()
for address in nearby_devices:
	if target_name == lookup_name( address ):
		target_address = address
		break
	
if target_address is None:
	print "Could not find bluetooth device: " + target_name
	sys.exit(0)

print "Bluetooth device " + target_name + " found with address: " + target_address

service_matches = find_service(uuid = uuid, address = target_address)

if len(service_matches) == 0:
	print("couldn't find it dawg")
	sys.exit(0)
	
port = service_matches[0]["port"]
name = service_matches[0]["name"]
host = service_matches[0]["host"]

print "connecting to " + name + " " + host

sock=BluetoothSocket(RFComm)
sock.connect((host, port))

while True:
	data = input()
	if len(data) == 0: break
	
sock.close()
