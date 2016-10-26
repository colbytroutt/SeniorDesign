from bluetooth import *
import threading
import commands

class ClientConnection(threading.Thread):

	def __init__(self, socket, info):
		threading.Thread.__init__(self)
		self.socket = socket
		self.info =  info
		self.setDaemon(True)
		self.start()
	
	def run(self):
		while True:
			try:
				data = self.socket.recv(1024).split(" ")
				if len(data) == 0: break
				self.proccessData(data)
			except IOError:
				break
		
		self.socket.close()
		print self.info, "disconnected."
		
	def proccessData(self, data):
		if(data[0] != None):
			try:
				func = commands.functions[data[0]]
				if(func != None):
					func(self, data)
			except:
				return

class Server(threading.Thread):
	
	def __init__(self, bluetoothName, uuid):
		threading.Thread.__init__(self)
		self.bluetoothName = bluetoothName
		self.uuid = uuid
		
	def start(self):

		#advertise bluetooth server
		threading.Thread.__init__(self)
		serverSocket = BluetoothSocket(RFCOMM)
		serverSocket.bind(("",PORT_ANY))
		serverSocket.listen(1)
		port = serverSocket.getsockname()[1]
		advertise_service(	serverSocket, self.bluetoothName,
							service_id = self.uuid,
							service_classes = [self.uuid, SERIAL_PORT_CLASS],
							profiles = [SERIAL_PORT_PROFILE])
						
		self.serverSocket = serverSocket
		
		#listen for connections
		self.setDaemon(True)
		threading.Thread.start(self)
	
	def run(self):
	
		while True:
			try:
				clientSocket, clientInfo = self.serverSocket.accept()
				print "Accepted connection from ", clientInfo
				ClientConnection(clientSocket, clientInfo)
			except IOError:
				break
	
	def stop(self):
		self.serverSocket.close()