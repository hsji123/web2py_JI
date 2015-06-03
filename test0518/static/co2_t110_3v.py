## This code for T100, ELT CO2 sensor
## Please see details for the CO2 sensor : ....

import serial,os,time
import sys
import RPi.GPIO as GPIO
import logging 
import logging.handlers 

DEBUG_PRINT = 1
SERIAL_READ_BYTE = 12
FILEMAXBYTE = 1024 * 1024 * 100 #100MB
LOG_PATH = './log_tos.log'

level = 0
ppm = 0

def led0On():
	GPIO.output(18, True)
def led1On():
	GPIO.output(23, True)
def led2On():
	GPIO.output(24, True)
def led3On():
	GPIO.output(25, True)

def led0Off():
	GPIO.output(18, False)
def led1Off():
	GPIO.output(23, False)
def led2Off():
	GPIO.output(24, False)
def led3Off():
	GPIO.output(25, False)
def ledAllOff():
	led0Off()
	led1Off()
	led2Off()
	led3Off()
def ledAllOn():
	led0On()
	led1On()
	led2On()
	led3On()


# check length, alignment of incoming packet string
def syncfind():
	index = 0
	alignment = 0
	while 1:
		in_byte = serial_in_device.read(1)
# packet[8] should be 'm'
# end of packet is packet[10]
		if in_byte is 'm' :
			#print 'idx =', index, in_byte
			alignment = 8
		if alignment is 10 : 
			alignment = 1
			index = 0
			break
		elif alignment > 0 :
			alignment += 1
		index += 1

def checkAlignment(incoming):
	idxNum = incoming.find('m')
	# idxNum is 9, correct
	offset = idxNum - 9	
	if offset > 0 :
		new_str = incoming[offset:]
		new_str = new_str + incoming[:offset]
	if offset < 0 :
		offset = 12 + offset 
		new_str = incoming[offset:]
		new_str = new_str + incoming[:offset]
	return new_str
	
def init_process():
	print " "
	print "MSG - [T110 CO2 Sensor] Please check log file : ", LOG_PATH
	print "MSG - now starting to read SERIAL PORT"
	print " "
	# HW setup, GPIO
	GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.OUT)
	GPIO.setup(23, GPIO.OUT)
	GPIO.setup(24, GPIO.OUT)
	GPIO.setup(25, GPIO.OUT)
	logger.info(' *start* GPIO all set, trying to open serial port, SW starting ')
	ledAllOn()

######################################################################
# START Here. Main
######################################################################

# set logger file
logger = logging.getLogger("CO2_T110")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=FILEMAXBYTE,backupCount=10)
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

#consoleHandler = logging.StreamHandler()
#consoleHandler.setLevel(logging.DEBUG)
#consoleHandler.setFormatter(formatter)
#logger.addHandler(consoleHandler)

# call raspi init...
init_process()

# open RASPI serial device, 38400
try:
	serial_in_device = serial.Serial('/dev/ttyAMA0',38400)
except serial.SerialException, e:
	logger.error("Serial port open error")
	led0Off()
	led1Off()
	led2Off()
	led3Off()

while 1:
	try:
		in_byte = serial_in_device.read(SERIAL_READ_BYTE) 
		pos = 0
	except serial.SerialException, e:
		led0Off()
		led1Off()
		led2Off()
		led3Off()
	if not (len(in_byte) is SERIAL_READ_BYTE) : 
		logger.error("Serial packet size is strange, %d, expected size is %d" % (len(in_byte),SERIAL_READ_BYTE))
		print 'serial byte read count error'
		continue
	# sometimes, 12 byte alighn is in-correct
	# espacially run on /etc/rc.local
	if not in_byte[9] is 'm':
		shift_byte = checkAlignment(in_byte)
		in_byte = shift_byte
		
	if ('ppm' in in_byte):
		if DEBUG_PRINT :
			print '-----\/---------\/------ DEBUG_PRINT set -----\/---------\/------ '
			for byte in in_byte :
				print "serial_in_byte[%d]: " %pos,
				pos += 1
				if ord(byte) is 0x0d :
					print "escape:", '0x0d'," Hex: ", byte.encode('hex')
					continue
				elif ord(byte) is 0x0a :
					print "escape:", '0x0a'," Hex: ", byte.encode('hex')
					continue
				print " String:", byte,  "    Hex: ", byte.encode('hex')
		if not (in_byte[2] is ' ') :
			ppm += (int(in_byte[2])) * 1000
		if not (in_byte[3] is ' ') :
			ppm += (int(in_byte[3])) * 100
		if not (in_byte[4] is ' ') :
			ppm += (int(in_byte[4])) * 10
		if not (in_byte[5] is ' ') :
			ppm += (int(in_byte[5]))  

		logline = 'CO2 Level is '+ str(ppm) + ' ppm' 
		#now = time.localtime()
		#now_str = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
		#logline += now_str
		if DEBUG_PRINT :
			print logline
		if ppm > 2500 : 
			logger.error("%s", logline)
		else :
			logger.info("%s", logline)

# level = 1, 0~1000 ppm,    no- LED
# level = 2, 1000~1150 ppm, 1 - LED
# level = 3, 1150~1300 ppm, 2 - LED
# level = 4, 1300~1700 ppm, 3 - LED
# level = 5, 1750~ ppm,     4 - LED

	if ppm < 1000 :  
		led0Off()
		led1Off()
		led2Off()
		led3Off()
	elif ppm < 1150 :  
		led0On()
		led1Off()
		led2Off()
		led3Off()
	elif ppm < 1300 :  
		led0On()
		led1On()
		led2Off()
		led3Off()
	elif ppm < 1700 :  
		led0On()
		led1On()
		led2On()
		led3Off()
	elif ppm >= 1700 :  
		led0On()
		led1On()
		led2On()
		led3On()
	ppm = 0
	time.sleep(10)
GPIO.cleanup()

