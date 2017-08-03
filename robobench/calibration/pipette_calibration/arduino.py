import serial
import time
from opentrons import robot

def opentrons_connect(ignore=''):
    try:
        # physical robot
        ports = robot.get_serial_ports_list()
        print(ports)
        for port in ports:
        	if port == ignore:
        		continue
        	robot.connect(port)
        	break

    except IndexError:
        # simulator
        robot.connect('Virtual Smoothie')
        robot.home(now=True)


# returns a string of the pressure reading form the arduino
def extract_val_str(line):
	replaced = line.replace('b','')
	replaced = replaced.replace('\'','')
	replaced = replaced.replace('\\','')
	replaced = replaced.replace('r','')
	replaced = replaced.replace('n','')
	replaced = replaced.rstrip()
	return replaced

ARDUINO_PORT = 'COM5'

opentrons_connect(ignore=ARDUINO_PORT)
robot.home('b')
# robot._driver.move_plunger(mode='absolute',b=0)

ser = serial.Serial(ARDUINO_PORT, 9600, timeout=0)
time.sleep(1.5)

# build pipette force curve
for j in range(0, 35, 1):
	# move pipette plunger
	robot._driver.move_plunger(mode='absolute',b=j)

	begin = time.time()
	while time.time() - begin < 2:
		line = ser.readline()
		val = extract_val_str(str(line))
		if len(val) > 0:
			print(j, val)