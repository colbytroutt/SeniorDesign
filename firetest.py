import hardware.hardwarecontroller as hc
import time

hc.connect()

hc.setBallDelay(115)
hc.setDartDelay(175)

hc.setBallFlywheel(True)
time.sleep(1)

for i in range(16):
	hc.fireBall()
	time.sleep(1)

hc.setBallFlywheel(False)
hc.setDartFlywheel(True)
time.sleep(1)

for i in range(8):
	hc.fireDart()
	time.sleep(1)

hc.setDartFlywheel(False)
