import tornado.ioloop
import tornado.web
import tornado.websocket

import thread
import time
import os

d = None
clients = set()

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render(os.path.dirname(os.path.abspath(__file__)) + "/" + "templates/index.html")
		
class DataHandler(tornado.web.RequestHandler):
	def get(self):
		global d
		while d is None:
			pass
			
		self.write(d)

class SocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		global clients
		clients.add(self)

	def on_message(self, message):
		self.write_message(u"You said: " + message)

	def on_close(self):
		global clients
		clients.discard(self)
		print("WebSocket closed")
	
	#def get_compression_options():
	#	return {}
	
def make_app():
	return tornado.web.Application([
		(r"/", MainHandler),
		(r"/data", DataHandler),
		(r"/websocket", SocketHandler),
		(r"/css/(.*)", tornado.web.StaticFileHandler, {"path": os.path.dirname(os.path.abspath(__file__)) + "/" + "data/css"}),
		(r"/js/(.*)", tornado.web.StaticFileHandler, {"path": os.path.dirname(os.path.abspath(__file__)) + "/" + "data/js"}),
		(r"/images/(.*)", tornado.web.StaticFileHandler, {"path": os.path.dirname(os.path.abspath(__file__)) + "/" + "data/images"})
	])
	
def broadCastMessage(data):
	#global clients
	global d
	
	d = data

	#for client in clients:
	#	client.write_message(data)

def startServer():
	app = make_app()
	app.listen(8888)
	thread.start_new_thread(tornado.ioloop.IOLoop.current().start, ())
	
if __name__ == "__main__":
	import time
	startServer()
	while True:
		time.sleep(1000)
		pass