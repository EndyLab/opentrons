from opentrons import robot, instruments, containers
from digit_processing import read_scale
import cv2
import time

# assumes pipette already has watrer in tip and is calibrated
def measure(pipette, scale):
	# dispense onto scale
	pipette.blow_out(scale.wells(0))
	time.sleep(2)

	# get scale coords use deltas tpo get screen
	coords = get_coords()
	new_x = coords[0] + 10
	new_y = coords[1] - 90
	new_z = coords[2] - 5
	robot.move_head(x=new_x, y=new_y, z=new_z)

	# take a picture of the scale
	cap = cv2.VideoCapture(2)
	ret, frame = cap.read()

	# feed pic into code
	val = read_scale(frame)

	# return results
	return val

def calibrate(pipette, scale, water, tiprack):
	# calibrates pipette
	calibrate_plunger(pipette)

	# pick up tip
	pipette.pick_up_tip(tiprack[0])

	last_reading = 0
	readings = []
	for j in range(3):
		pipette.aspirate(200, water.wells(0))   
		val = measure(pipette, scale)
		
		tared = val - last_reading
		print(val, tared)
		readings.append(tared)
		last_reading = val

	total = 0
	for val in readings:
		total += val

	ave = float(total/len(readings))
	print("average out of 3:", ave)
	pipette.max_volume = ave
	pipette.update_calibrations()

def calibrate_plunger(pipette):
	pipette.calibrate_plunger(top=12, bottom=27, blow_out=33, drop_tip=34)
	pipette.update_calibrations()

def get_coords():
    Point = []
    curr_coords = robot._driver.get_head_position()
    curr_x = curr_coords['current'].coordinates.x
    curr_y = curr_coords['current'].coordinates.y
    curr_z = curr_coords['current'].coordinates.z
    pos = [curr_x, curr_y, curr_z]
    # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
    return pos
