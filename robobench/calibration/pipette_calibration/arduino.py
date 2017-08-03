import serial
import time
from opentrons import robot
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np
import sys
import getopt

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

params = ''
# cmdargs = str(sys.argv)[1:]
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:h', ['params=', 'help'])
except getopt.GetoptError:
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage()
        sys.exit(2)
    elif opt in ('-p', '--params'):
        params = arg
    else:
        usage()
        sys.exit(2)

if params != 'file':
	ARDUINO_PORT = 'COM5'

	opentrons_connect(ignore=ARDUINO_PORT)
	robot.home('b')
	# robot._driver.move_plunger(mode='absolute',b=0)

	ser = serial.Serial(ARDUINO_PORT, 9600, timeout=0)
	time.sleep(1.5)

	# build pipette force curve
	plunger_distance = []
	arduino_reading = []
	averages = []
	dist = np.linspace(0,35+1,num=100)
	for j in dist:
		if j == 35//4:
			print('25%% done')
		if j == 35//2:
			print('50%% done')
		if j == 35//4*3:
			print('75%% done')
		# move pipette plunger
		robot._driver.move_plunger(mode='absolute',b=j)

		begin = time.time()
		num_vals = 0
		total = 0
		while time.time() - begin < 5:
			line = ser.readline()
			val = extract_val_str(str(line))
			if len(val) > 0:
				plunger_distance.append(j)
				arduino_reading.append(int(val))
				num_vals += 1
				total += int(val)
				# print(j, val)
		averages.append(float(total/num_vals))

	x = np.array(plunger_distance)
	y = np.array(arduino_reading)
	ave = np.array(averages)

	# save data
	np.savetxt("plunger_distances.csv", x, delimiter=",")
	np.savetxt("arduino_readings.csv", y, delimiter=",")
	np.savetxt('ave_readings.csv', ave, delimiter=',')

else: 
	dist = np.linspace(0,35+1,num=100)
	x = np.genfromtxt('plunger_distances.csv', delimiter=',')
	y = np.genfromtxt('arduino_readings.csv', delimiter=',')
	averages = np.genfromtxt('ave_readings.csv', delimiter=',')

# curve fitting
y_spl = UnivariateSpline(x,y,s=0,k=4)
plt.plot(x,y,'ro',label = 'data')

# averages
plt.plot(dist,averages,'bo',label = 'ave')
spl = UnivariateSpline(dist, averages)
xs = np.linspace(dist[0], dist[-1], 1000)
plt.plot(xs, spl(xs), 'g', lw=3)

# 2nd derivative
y_spl_2d = spl.derivative(n=2)
deriv2 = y_spl_2d(xs)
plt.plot(xs,deriv2, 'y', lw=3)

# find maximums (3 points)
max_indices = np.argpartition(deriv2, -3)[-3:]
max_vals = deriv2[max_indices]


points = []
for i in range(len(max_vals)):
	points.append((max_indices[i], max_vals[i]))

points.sort(key=lambda tup: tup[1])
print(points)


# axis
plt.axis([0, 34, 0, 400])
plt.show()

