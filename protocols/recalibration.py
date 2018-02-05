from opentrons import robot, containers, instruments
import argparse
import sys

import json
import os
import glob
import re

import getch

port = os.environ["ROBOT_DEV"]
robot.connect(port)

p10_tiprack = containers.load('tiprack-10ul', "E2")

trash = containers.load('point', 'D1', 'holywastedplasticbatman')
uncalibrated = containers.load('point', 'B2','uncalibrated')
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
        elif c == "x":
            x = 1 
    p10.calibrate_position((container))

    return p10

robot.home()

p10.move_to(uncalibrated)
change_height(uncalibrated)
p10.move_to(uncalibrated)


input("old script?")



#
