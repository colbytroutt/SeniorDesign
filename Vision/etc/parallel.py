from multiprocessing import Process, Queue, Lock
from timeit import default_timer as timer

grayscaleImageQueueInput = Queue()
targetQueueOutput = Queue()
medicQueueOutput = Queue()
robotQueueOutput = Queue()

targetLock1 = Lock()
targetLock2 = Lock()
medicLock1 = Lock()
medicLock2 = Lock()
robotLock1 = Lock()
robotLock2 = Lock()

def foo(input, output, l, l2):
	
	while True:
		l.acquire()
		output.put(input.get() + 1)
		
		l2.release()
		
def detectAllTargetsParallel2(grayscaleImage):

	global grayscaleImageQueueInput
	global targetLock1
	global targetLock2
	global medicLock1
	global medicLock2
	global robotLock1
	global robotLock2

	grayscaleImageQueueInput.put(grayscaleImage)

	print("here1")
	
	targetLock1.release()
	medicLock1.release()
	robotLock1.release()

	print("here2")
	
	targetLock2.acquire()
	medicLock2.acquire()
	robotLock2.acquire()

	print("here5")
	
	#return (targetQueueOutput.get(), medicQueueOutput.get(), robotQueueOutput.get())
	return (numpy.array([]),numpy.array([]),numpy.array([]))
	
def detectRobotsParallel(lock1, lock2, inputQueue, outputQueue):
	
	while True:
		lock1.acquire()
		outputQueue.put(detectTargets(outputQueue.get()))
		lock2.release()

def initParallelization2():

	global grayscaleImageQueueInput
	global targetQueueOutput
	global medicQueueOutput
	global robotQueueOutput
	global targetLock1
	global targetLock2
	global medicLock1
	global medicLock2
	global robotLock1
	global robotLock2

	targetLock1.acquire()
	targetLock2.acquire()
	medicLock1.acquire()
	medicLock2.acquire()
	robotLock1.acquire()
	robotLock2.acquire()

	targetProcess = Process(target=detectAllTargetsParallel, args=(targetLock1, targetLock2, grayscaleImageQueueInput, targetQueueOutput))
	medicProcess = Process(target=detectMedicsParallel, args=(medicLock1, medicLock2, grayscaleImageQueueInput, medicQueueOutput))
	robotProcess = Process(target=detectRobotsParallel, args=(robotLock1, robotLock2, grayscaleImageQueueInput, robotQueueOutput))

	targetProcess.start()
	medicProcess.start()
	robotProcess.start()		
		
if __name__ == '__main__':
	n = 0
	
	input = Queue()
	output = Queue()
	
	lTarget = Lock()
	lMedic = Lock()
	lRobot = Lock()
	l2Target = Lock()
	l2Medic = Lock()
	l2Robot = Lock()
	l.acquire()
	l2.acquire()
	
	start = timer()
	p = Process(target=foo, args=(input, output, l, l2))
	p.start()
	print("initialization: " + str((timer()-start)*1000))
	
	while True:
		n = n + 1
		start = timer()
		input.put(n)
		
		#allow threads to process
		l.release()
		
		#wait for everything to finish
		l2target.acquire()
		l2medic.acquire()
		l2robot.acquire()
		
		print(output.get())
		print("runtime: " + str((timer()-start)*1000))
	
	p.join()
