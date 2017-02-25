# main.py

from flask import Flask, render_template, Response
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

def broadcastData():
	socketio.emit('videostream', {'data': 42})			
					
if __name__ == "__main__":
	socketio.run(app)
	