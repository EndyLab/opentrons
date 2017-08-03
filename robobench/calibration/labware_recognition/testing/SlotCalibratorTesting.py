from SlotCalibrator import SlotCalibrator
from opentrons import robot, containers, instruments


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
container_dict = calibrator.calibrate(pipette, {'plateA':'96-flat'})
plateA = container_dict['plateA']
pipette.move_to(plateA.wells('A1'))

