from get_images import take_pic
from opentrons import robot, instruments, containers
import random
import time

def opentrons_connect(home=False):
    try:
        # physical robot
        ports = robot.get_serial_ports_list()
        print(ports)
        robot.connect(ports[0])
    except IndexError:
        # simulator
        robot.connect('Virtual Smoothie')
        robot.home(now=True)
    if home == True:
    	robot.home('xyzab')
    	print('robot homed')

def get_coords():
    Point = []
    curr_coords = robot._driver.get_head_position()
    curr_x = curr_coords['current'].coordinates.x
    curr_y = curr_coords['current'].coordinates.y
    curr_z = curr_coords['current'].coordinates.z
    pos = [curr_x, curr_y, curr_z]
    # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
    return pos

if __name__ == '__main__':
	img_dir = 'C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/screen'
	opentrons_connect(home=True)

	# calibrate stuff on the deck
	print('loading labware')
	tiprack = containers.load('tiprack-200ul', 'A1')
	water = containers.load('point', 'A1', 'water')
	scale = containers.load('point', 'A1', 'scale')
	scale_screen = containers.load('point', 'A1', 'screen')
	p200 = instruments.Pipette(axis='b', max_volume=200)

	print('calibrate plunger')
	p200.calibrate_plunger(top=12, bottom=27, blow_out=33, drop_tip=34)
	p200.update_calibrations()

	# pick up tip
	print('picking up tip')
	p200.pick_up_tip(tiprack[0])
	# p200.pick_up_tip(water[0])
	# p200.pick_up_tip(scale[0])
	# p200.pick_up_tip(scale_screen[0])

	last_reading = 0
	readings = []

	print('beginning image collection')
	for i in range(50,200,5):
		p200.aspirate(i, water.wells(0))   
		p200.blow_out(scale.wells(0))
		time.sleep(2)
		p200.move_to(scale_screen)
		take_pic(2, 0, img_dir)

		# random xyz variations
		print('adding random xyz variations')
		for j in range(3):
			take_pic(2, 0, img_dir)
			coords = get_coords()
			new_x = coords[0] + random.uniform(-50, 70)
			new_y = coords[1] + random.uniform(-100, 70)
			# new_z = coords[2] + random.uniform(-100, 100)
			robot.move_head(x=new_x, y=new_y, z=coords[2])
			take_pic(2, 0, img_dir)
			
	robot.disconnect()


