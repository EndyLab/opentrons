import json
from opentrons import robot
from snapshot import read_scale

POS = 	{
			"blow_out": 0,
			"bottom": 0,
			"drop_tip": 0,
			"top": 0
		}

def get_coords():
    curr_coords = robot._driver.get_head_position()
    curr_x = curr_coords['current'].coordinates.x
    curr_y = curr_coords['current'].coordinates.y
    curr_z = curr_coords['current'].coordinates.z
    # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
    return [curr_x, curr_y, curr_z]

class PiBetter:
	instances = {}
	nameToVar = {}

	def __init__(self, name, axis, max_volume,pos=POS):
		self.name = name
		self.axis = axis
		self.max_volume = max_volume
		self.pos = pos

		self.var = self
		PiBetter.nameToVar[self.name] = self

		self.update()

	def delete(self):
		PiBetter.instances.pop(self.name, None)
		PiBetter.nameToVar.pop(self.name, None)
		del(self)

	def to_dict(self):
		data = 	{
					self.name: {
						'axis'		: self.axis,
						'max_volume': self.max_volume,
						'positions'	: self.pos
					}
				}
		return data

	def update(self):
		self.dict = self.to_dict()
		PiBetter.instances.update(self.dict)

	def get_max_volume(self):
		return self.max_volume

	def set_pos(self, posName, val):
		if posName in self.pos.keys():
			# FIXME
			# for some reason self.pos['posName'] = val changes 
			# the the pos dict for ALL instances of the class
			# this temp jank fix works though...
			# look at change_max_volume function for more weirdness...
			temp = {
				'top'		: self.pos['top'],
				'bottom'	: self.pos['bottom'],
				'drop_tip'	: self.pos['drop_tip'],
				'blow_out'	: self.pos['blow_out'],
				# replace old val with new
				posName		: val
			}
			self.pos = temp
			self.update()
			return 0
		return -1

	# but this works fine...
	def change_max_volume(self, vol):
		self.max_volume = vol
		self.update()

	def move_pipette(self, coords):
		x = coords[0]
		y = coords[1]
		z = coords[2]
		robot.move_head(x=x, y=y, z=z)

	def aspirate(self, vol, coords):
		if vol <= self.max_volume:
			# move plunger to first stop 
			top = self.pos['top']
			# robot._driver.move_plunger(mode='absolute',b=top)
			bottom = self.pos['bottom']
			# robot._driver.move_plunger(mode='absolute',b=bottom)

			travel = self.get_plunge_distance(vol)
			print('top - bottom:', bottom-top, 'travel distance:', travel)
			robot._driver.move_plunger(mode='absolute',b=top+travel)

			# go down to water source
			# coords = get_coords()
			# x = coords[0]
			# y = coords[1]
			# z = coords[2]
			self.move_pipette(coords)
			# robot.move_head(x=x, y=y, z=z-60)

			# pick up liquid
			robot._driver.move_plunger(mode='absolute',b=top)

			# move robot up
			# robot.move_head(x=x, y=y, z=z)
			# self.move_pipette(coords)

	def dispense(self, coords=[]):
		if len(coords) == 3:
			self.move_pipette(coords)

		# move plunger all the way down
		blow_out = self.pos['blow_out']
		robot._driver.move_plunger(mode='absolute',b=blow_out)

		# move plunger back up?
		top = self.pos['top']
		robot._driver.move_plunger(mode='absolute',b=top)

	def get_plunge_distance(self, vol):
	    """Calculate axis position for a given liquid volume.
	    Translates the passed liquid volume to absolute coordinates
	    on the axis associated with this pipette.
	    Calibration of the top and bottom positions are necessary for
	    these calculations to work.
	    """
	    percent = float(vol/self.max_volume)
	    top = self.pos['top']
	    bottom = self.pos['bottom']
	    travel = bottom - top
	    if travel <= 0:
	        robot.add_warning('Plunger calibrated incorrectly')
	    return travel * percent

# PiBetter class demo
def demo():
	# making pipette instances
	test = PiBetter('pip1','a',100)
	test1 = PiBetter('pip2','b',200)

	# changing position
	test1.set_pos('drop_tip',20)
	test.set_pos('top', 10)

	# changing volume
	test.change_max_volume(200)

	# deleting an instance
	PiBetter.nameToVar['pip1'].delete()
	print("name",test.name)

	pipData = PiBetter.instances
	pipList = PiBetter.nameToVar
	print(pipData)
	print(pipList)
	# write to .json file
	with open('data.json', 'w+') as f:
	    json.dump(pipData, f,sort_keys=True, indent=4)

def removePipette(pipette):
	pipette.delete()
	del pipette

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

def to_vol_measurement(scale_reading):
	# this particular scale has a decimal after the 3rd digit from the right
	decimal_pos = 3
	factor = 10**decimal_pos
	val = 0
	for digit in scale_reading:
		val = val*10 + digit

	# vol in liters
	return val

def calibrate(pipette, vol):
	scale_coords = [150, 220.1, 5]
	water_coords = [250, 220.1, -30]
	pipette.aspirate(vol, [water_coords[0], water_coords[1], water_coords[2]-10])

	# move to scale
	pipette.dispense(scale_coords)
	scale_reading = read_scale()
	while scale_reading == -1:
		scale_reading = read_scale()

	scale_val = to_vol_measurement(scale_reading)
	print(scale_reading)
	print(scale_val)

if __name__ == '__main__':
	# demo()
	opentrons_connect()

	with open('data.json') as json_data:
		pipData = json.load(json_data)

	# use json to instantiate pipettes
	pipettes = []
	for name in pipData.keys():
		data = pipData[name]
		pipettes.append(PiBetter(name, data['axis'], data['max_volume'], data['positions']))		

	# print(PiBetter.nameToVar)
	"""
	robot._driver.move_plunger(mode='relative', a=1)
	strs = robot._driver.get_plunger_positions()
	print(strs)
	"""
	# home robot
	# robot._driver.home('z')
	# robot._driver.home('x', 'y', 'b', 'a')
	# [95.004, 405.0, 95.0]

	# robot._driver.home('b','a')

	p = PiBetter.nameToVar['pip2']
	test_vol = p.get_max_volume()
	calibrate(p, test_vol)
	calibrate(p, 100)

	# shell for debugging
	"""
	cmd = ''
	while cmd != 'q':
		cmd = input('input (q to quit): ')

		if cmd == 'q':
			break

		elif cmd == 'home':
			robot.home('xyzab')
		# save calibration pos
		elif cmd == 'save':
			temp = input('which pos to save calibration: ')
			plungerPos = robot._driver.get_plunger_positions()
			print(plungerPos)
			p.set_pos(temp,plungerPos['current']['b'])

		# remove a pipette
		elif cmd == 'rm':
			temp = input('name of pipette to delete: ')
			removePipette(PiBetter.nameToVar[temp])

		# move to calibrated positions
		elif cmd == 'move':
			temp = input('which position: ')
			pos = PiBetter.instances['pip2']['positions'][temp]
			robot._driver.move_plunger(mode='absolute',b=pos)

		# move to specific coord
		elif cmd.replace('.','',1).isdigit():
			robot._driver.move_plunger(mode='absolute',b=float(cmd))

		else:
			print('not a valid input')
	"""

	# write to .json file
	with open('data.json', 'w+') as f:
	    json.dump(PiBetter.instances, f,sort_keys=True, indent=4)

	robot.disconnect()
