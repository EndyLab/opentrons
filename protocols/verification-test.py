#File: prVerificationTest.py
#
#This is a plate reader dye test intended to measure and verify the precision and accuracy
#of an Opentrons robot. Ten 96-well plates are filled with an equal amount of dye (water
#with food coloring), and then a plate reader is used to measure the amount of dye that is
#actually contained in each well.

from opentrons import Robot, containers, instruments

robot = Robot()
robot.reset()

#CONTAINERS=====================================================================================
#Trash
trash = containers.load('point', 'A3', 'Trash')
#Tip Rack: p200 tips
tiprack = containers.load('tiprack-200ul', 'B3', 'p200 tip rack')
#Dye Source: 12-row trough
trough = containers.load('trough-12row', 'C3', 'Trough')
#Output: 10 96-well plates
#plate1 = containers.load('96-PCR-flat', 'D3', 'Plate 1')
#plate2 = containers.load('96-PCR-flat', 'E3', 'Plate 2')
plate3 = containers.load('96-PCR-flat', 'B2', 'Plate 3')
#plate4 = containers.load('96-PCR-flat', 'C2', 'Plate 4')
#plate5 = containers.load('96-PCR-flat', 'D2', 'Plate 5')
#plate6 = containers.load('96-PCR-flat', 'E2', 'Plate 6')
#plate7 = containers.load('96-PCR-flat', 'B1', 'Plate 7')
#plate8 = containers.load('96-PCR-flat', 'C1', 'Plate 8')
#plate9 = containers.load('96-PCR-flat', 'D1', 'Plate 9')
#plate10 = containers.load('96-PCR-flat', 'E1', 'Plate 10')

#INSTRUMENTS====================================================================================
#PipetteA: p200 single channel
p200 = instruments.Pipette(
    name="p200",
    trash_container=trash,
    tip_racks=[tiprack],
    min_volume=20,
    max_volume=200.7,
    axis="b",
)

#ACTIONS========================================================================================
#home the robot axes in an order appropriate for either the OT-One or RoboBench
#robot.home('z', enqueue=True)
#robot.home('y', enqueue=True)
#robot.home('x', enqueue=True)

#first five plates use a transfer
#p200.transfer(
#	20,
#	trough.wells('A1'),
#	plate1.rows('1', to='12'),
#	blow_out=True
#)

#p200.transfer(
#	20,
#	trough.wells('A2'),
#	plate2.rows('1', to='12'),
#	blow_out=True
#)

p200.transfer(
	20,
	trough.wells('A3'),
	plate3.rows('1'),
	blow_out=True,
	touch_tip=True
)
p200.transfer(
	20,
	trough.wells('A3'),
	plate3.rows('2'),
	blow_out=True,
	touch_tip=True
)
p200.transfer(
	20,
	trough.wells('A3'),
	plate3.rows('3'),
	blow_out=True,
	touch_tip=True
)
p200.transfer(
	20,
	trough.wells('A3'),
	plate3.rows('4'),
	blow_out=True,
	touch_tip=True
)
p200.transfer(
	20,
	trough.wells('A3'),
	plate3.rows('5'),
	blow_out=True,
	touch_tip=True
)
p200.transfer(
	20,
	trough.wells('A3'),
	plate3.rows('6'),
	blow_out=True,
	touch_tip=True
)

p200.distribute(
	20,
	trough.wells('A3'),
	plate3.rows('7'),
	blow_out=True,
	touch_tip=True
)
p200.distribute(
	20,
	trough.wells('A3'),
	plate3.rows('8'),
	blow_out=True,
	touch_tip=True
)
p200.distribute(
	20,
	trough.wells('A3'),
	plate3.rows('9'),
	blow_out=True,
	touch_tip=True
)
p200.distribute(
	20,
	trough.wells('A3'),
	plate3.rows('10'),
	blow_out=True,
	touch_tip=True
)
p200.distribute(
	20,
	trough.wells('A3'),
	plate3.rows('11'),
	blow_out=True,
	touch_tip=True
)
p200.distribute(
	20,
	trough.wells('A3'),
	plate3.rows('12'),
	blow_out=True,
	touch_tip=True
)

robot.simulate()

#p200.transfer(
#	20,
#	trough.wells('A4'),
#	plate4.rows('1', to='12'),
#	blow_out=True
#)

#p200.transfer(
#	20,
#	trough.wells('A5'),
#	plate5.rows('1', to='12'),
#	blow_out=True
#)


#second five plates use distribute
#p200.distribute(
#	20,
#	trough.wells('A6'),
#	plate6.rows('1', to='12'),
#	touch_tip=True
#)

#p200.distribute(
#	20,
#	trough.wells('A7'),
#	plate7.rows('1', to='12'),
#	touch_tip=True
#)

#p200.distribute(
#	20,
#	trough.wells('A8'),
#	plate8.rows('1', to='12'),
#	touch_tip=True
#)

#p200.distribute(
#	20,
#	trough.wells('A9'),
#	plate9.rows('1', to='12'),
#	touch_tip=True
#)

#p200.distribute(
#	20,
#	trough.wells('A10'),
#	plate10.rows('1', to='12'),
#	touch_tip=True
#)
