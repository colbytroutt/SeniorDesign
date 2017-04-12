#!/usr/bin/env python

from __future__ import division
import serial
import minimalmodbus
import os
import time

def main():
	minimalmodbus.BAUDRATE = 115200   # Baud
	minimalmodbus.BYTESIZE = 8
	minimalmodbus.PARITY = 'N'
	minimalmodbus.STOPBITS  = 1
	minimalmodbus.TIMEOUT = 0.05   # seconds
	minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = False

	mmb = minimalmodbus.Instrument("/dev/bus/usb/001/010", 1, 'rtu')

	temp = mmb.read_register(22, 0, 4, True)

	time.sleep(0.1) # ARBITRARY SLEEP REQUIRED WHY?

	num_detections = mmb.read_register(23, 0, 4)
	print "num_detections: %d" % num_detections

	dist_leddar = mmb.read_register(24, 0, 4)
	print "distance: %d" % dist_leddar 

if __name__ == "__main__":
	main()
