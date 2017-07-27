import json
from opentrons import robot

POS = 	{
			"blow_out": 0,
			"bottom": 0,
			"drop_tip": 0,
			"top": 0
		}

class BetterPipette:
	instances = {}
	nameToVar = {}

	def __init__(self, name, axis, max_volume, pos=POS):
		self.name = name
		self.axis = axis
		self.max_volume = max_volume
		self.pos = pos

		self.var = self
		BetterPipette.nameToVar[self.name] = self

		self.update()

	def delete(self):
		BetterPipette.instances.pop(self.name, None)
		BetterPipette.nameToVar.pop(self.name, None)
		del(self)

	def toDict(self):
		data = 	{
					self.name: {
						'axis'		: self.axis,
						'max_volume': self.max_volume,
						'positions'	: self.pos
					}
				}
		return data

	def update(self):
		self.dict = self.toDict()
		BetterPipette.instances.update(self.dict)

	def setPos(self, posName, val):
		if posName in self.pos.keys():
			# FIXME
			# for some reason self.pos['posName'] = val changes 
			# the the pos dict for ALL instances of the class
			# this temp jank fix works though...
			# look at changeVolume function for more weirdness...
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
	def changeVolume(self, vol):
		self.max_volume = vol
		self.update()


# with open('data.json') as json_data:
#     pipData = json.load(json_data)

# BetterPipette class demo
def demo():
	# making pipette instances
	test = BetterPipette('pip1','a',100)
	test1 = BetterPipette('pip2','b',200)

	# changing position
	test1.setPos('drop_tip',20)
	test.setPos('top', 10)

	# changing volume
	test.changeVolume(200)

	# deleting an instance
	BetterPipette.nameToVar['pip1'].delete()
	print("name",test.name)

	pipData = BetterPipette.instances
	pipList = BetterPipette.nameToVar
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

if __name__ == '__main__':
	# demo()
	opentrons_connect()

	# making pipette instances
	test = BetterPipette('pip1','a',100)
	test1 = BetterPipette('pip2','b',200)
	# print(BetterPipette.nameToVar)

	# changing position
	test1.setPos('drop_tip',20)
	test.setPos('top', 10)
	test.changeVolume(200)
	# removePipette(test1)

	# with open('data.json') as json_data:
	# 	pipData = json.load(json_data)

	"""
	robot._driver.move_plunger(mode='relative', a=1)
	strs = robot._driver.get_plunger_positions()
	print(strs)
	"""
	cmd = ''
	while cmd != 'q':
		cmd = input('input (q to quit): ')

		if cmd == 'q':
			break

		# save calibration pos
		elif cmd == 'save':
			temp = input('which pos to save calibration: ')
			plungerPos = robot._driver.get_plunger_positions()
			print(plungerPos)
			test1.setPos(temp,plungerPos['current']['b'])

		# remove a pipette
		elif cmd == 'rm':
			temp = input('name of pipette to delete: ')
			removePipette(BetterPipette.nameToVar[temp])

		# move to calibrated positions
		elif cmd == 'move':
			temp = input('which position: ')
			pos = BetterPipette.instances['pip2']['positions'][temp]
			robot._driver.move_plunger(mode='absolute',b=pos)

		# move to specific coord
		elif cmd.replace('.','',1).isdigit():
			robot._driver.move_plunger(mode='absolute',b=float(cmd))

		else:
			print('not a valid input')

	robot.disconnect()
	# write to .json file
	with open('data.json', 'w+') as f:
	    json.dump(BetterPipette.instances, f,sort_keys=True, indent=4)
