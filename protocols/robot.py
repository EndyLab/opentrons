#!/usr/bin/python3

from opentrons import robot, containers, instruments
import os
import IPython
import glob

# Configure the robot
# Set up your deck layout here.

#  Layout:
#    A     B       C      D      E
#  3 p200          pcr    pcr    p10
#  2               pcr    pcr    p10
#  1       reagt          trash  p10
#

p10s_tipracks = [containers.load('tiprack-10ul', 'E3')]
p10_tipracks = [containers.load('tiprack-10ul', 'E2')]
p200_tipracks = [containers.load('tiprack-200ul', 'A3')]

pcrs = [containers.load('96-PCR-tall', 'C2'),
  containers.load('96-PCR-tall', 'C3'),
  containers.load('96-PCR-tall', 'D2'),
  containers.load('96-PCR-tall', 'D3')]

reagents = containers.load('tube-rack-2ml', 'B1')

trash = containers.load('point', 'D1', 'holywastedplasticbatman')

p10s = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=p10s_tipracks,
    trash_container=trash,
    channels=1,
    name='p10-8s'
)

p10 = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=p10_tipracks,
    trash_container=trash,
    channels=8,
    name='p10-8'
)

p200 = instruments.Pipette(
    axis='b',
    max_volume=200,
    min_volume=20,
    tip_racks=p200_tipracks,
    trash_container=trash,
    channels=1,
    name='p200-1'
)

# Go higher between wells
robot.arc_height=20

# Determine the robot device we should be using.
if not 'ROBOT_DEV' in os.environ:
    print("Please select a robot device")
    devs = glob.glob("/dev/ttyACM*")
    for i, dev in enumerate(devs):
        print("  {}: {}".format(i, dev))
    robot_dev = input()
    if robot_dev.isdigit():
        robot_dev = devs[int(robot_dev)]

    print()
else:
    robot_dev = os.environ['ROBOT_DEV']

print("Connecting to robot {}".format(robot_dev))
robot.connect(robot_dev)

IPython.embed()
