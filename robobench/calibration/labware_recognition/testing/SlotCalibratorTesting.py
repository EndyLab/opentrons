from SlotCalibrator import SlotCalibrator
from opentrons import robot, containers, instruments
import sys


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

opentrons_connect()

# How to set tiprack after?
pipette = instruments.Pipette(axis='b', max_volume=200)

calibrator = SlotCalibrator()
calibrator.initialize()
container_dict = calibrator.calibrate(pipette, {'plateA':'96-flat', 'tips':'tiprack-200ul', 'trough':'trough', 'scale':'scale', 'trash':'trash'})
while 'error' in container_dict.keys():
	print('Error: {}'.format(container_dict['error']))
	cont = input('Retry? [y/n]')
	if cont == 'y':
		container_dict = calibrator.calibrate(pipette, {'plateA':'96-flat'})
	else:
		sys.exit(0)
print(container_dict)
plateA = container_dict['plateA']
tips = container_dict['tips']
trough = container_dict['trough']
scale = container_dict['scale']
trash = container_dict['trash']
pipette.pick_up_tip(tips.wells('A1'))
pipette.aspirate(100, trough)
pipette.dispense(plateA.wells('A1'))
robot.run()

