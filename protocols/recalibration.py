from opentrons import robot, containers, instruments
import argparse
import sys

import json
import os
import glob
import re

import getch
import IPython

port = os.environ["ROBOT_DEV"]
robot.connect(port)

p10_tiprack = containers.load('tiprack-10ul', "E2")

trash = containers.load('point', 'D1', 'holywastedplasticbatman')
uncalibrated = containers.load('96-deep-well', 'B2','uncalibrated')
calibrated = containers.load('point', 'D2','calibrated')

p10 = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=p10_tiprack,
    trash_container=trash,
    channels=8,
    name='p10-8'
    )

def change_height(container):
    x = 0
    print("h:+0.5,j:+0.1,k:-0.1,l:-0.5")
    while x == 0:
        c = getch.getch()
        if c == "h":
            p10.robot._driver.move(z=0.5,mode="relative")
        elif c == "j":
            p10.robot._driver.move(z=0.1,mode="relative")
        elif c == "k":
            p10.robot._driver.move(z=-0.1,mode="relative")
        elif c == "l":
            p10.robot._driver.move(z=-0.5,mode="relative")
        elif c == "p":
            p10.robot._driver.move(z=30,mode="relative")
        elif c == "x":
            x = 1 
    p10.calibrate_position((uncalibrated, uncalibrated[0].from_center(x=0, y=0, z=-1, reference=uncalibrated)))


#robot.home()
#IPython.embed()

p10.move_to(uncalibrated[0].bottom())
IPython.embed()
print("reached plate")
#change_height(uncalibrated)
print(uncalibrated)
#p10.move_to(calibrated)
p10.move_to(uncalibrated[0].bottom())





#
