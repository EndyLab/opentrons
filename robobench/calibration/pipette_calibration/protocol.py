from opentrons import robot
from opentrons import instruments
from opentrons import containers
from opentrons.containers.placeable import unpack_location, Placeable
from snapshot import read_scale
import time

def opentrons_connect():
    try:
        # physical robot
        ports = robot.get_serial_ports_list()
        print(ports)
        robot.connect(ports[0])
    except IndexError:
        # simulator
        robot.connect('Virtual Smoothie')
        robot.home(now=True)

    # robot.home('xyzab')
    # pipette = instruments.Pipette(axis='a')

scale_coords = [150, 220.1, 5]
water_coords = [250, 220.1, -30]

def get_coords():
    Point = []
    curr_coords = robot._driver.get_head_position()
    curr_x = curr_coords['current'].coordinates.x
    curr_y = curr_coords['current'].coordinates.y
    curr_z = curr_coords['current'].coordinates.z
    pos = [curr_x, curr_y, curr_z]
    # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
    return pos

def to_vol_measurement(scale_reading):
	# this particular scale has a decimal after the 3rd digit from the right
	decimal_pos = 3
	factor = 10**decimal_pos
	val = 0
	for digit in scale_reading:
		val = val*10 + digit

	# vol in micro liters
	return val

def calibrate_plunger(pipette):
	pipette.calibrate_plunger(top=12, bottom=27, blow_out=33, drop_tip=34)
	pipette.update_calibrations()

def pipscale(pipette, scale, tiprack, trough, trash):
	# calibrates pipette
	calibrate_plunger(pipette)

	# pick up tip
	pipette.pick_up_tip(tiprack[0])

	last_reading = 0
	readings = []
	for j in range(3):
		pipette.aspirate(200, trough.wells(0))   
		pipette.blow_out(scale.wells(0))
		time.sleep(2)

		# get scale coords use deltas tpo get screen
		coords = get_coords()
		# pipette.move_to(scale_screen)
		new_x = coords[0] + 10
		new_y = coords[1] - 90
		new_z = coords[2] - 5
		robot.move_head(x=new_x, y=new_y, z=new_z)
		scale_reading = read_scale(debug='on')
		while scale_reading == -1:
			scale_reading = read_scale(debug='on')

		amount = to_vol_measurement(scale_reading)
		tared = amount - last_reading
		print(amount, tared)
		readings.append(tared)
		last_reading = amount

	total = 0
	for val in readings:
		total += val

	ave = float(total/len(readings))
	print("average out of 3:", ave)
	pipette.max_volume = ave
	print(pipette.max_volume)
	pipette.update_calibrations()

if __name__ == '__main__':
	opentrons_connect()
	robot.home('xyzab')
	# calibrate stuff on the deck

	tiprack = containers.load('tiprack-200ul', 'A1')
	water = containers.load('point', 'A1', 'water')
	scale = containers.load('point', 'A1', 'scale')
	scale_screen = containers.load('point', 'A1', 'screen')
	p200 = instruments.Pipette(axis='b', max_volume=200)

	p200.calibrate_plunger(top=12, bottom=27, blow_out=33, drop_tip=34)
	p200.update_calibrations()

	# pick up tip
	p200.pick_up_tip(tiprack[0])
	# p200.pick_up_tip(scale_screen)
	last_reading = 0
	readings = []
	for j in range(3):
		p200.aspirate(200, water.wells(0))   
		p200.blow_out(scale.wells(0))
		time.sleep(2)
		p200.move_to(scale_screen)
		scale_reading = read_scale(debug='on')
		while scale_reading == -1:
			scale_reading = read_scale(debug='on')

		amount = to_vol_measurement(scale_reading)
		tared = amount - last_reading
		print(amount, tared)
		readings.append(tared)
		last_reading = amount

	total = 0
	for val in readings:
		total += val

	ave = float(total/len(readings))
	print("average out of 3:", ave)
	p200.max_volume = ave
	print(p200.max_volume)
	p200.update_calibrations()

	robot.disconnect()


