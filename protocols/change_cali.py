from opentrons import robot, containers, instruments
import argparse
import sys

import json
import os
import glob
import re

def change_calibration(turret,pipette,slot,container,axis,amount):
    with open("../robots/da5id_dup/calibrations/calibrations.json","r") as json_file:
        calibrations = json.load(json_file)
        pipette = turret+":"+pipette
        current_cali = calibrations["data"][pipette]["calibration_data"][slot]["children"][container]["delta"]
        print(current_cali)
        y_cali, z_cali, x_cali = re.match(
            r'{"y": (-?[0-9]+\S[0-9]+), "z": (-?[0-9]+\S[0-9]+), "x": (-?[0-9]+\S[0-9]+)}',
            current_cali).groups()
        cali = dict({"y" : float(y_cali),"z" : float(z_cali),"x" : float(x_cali)})
        cali[axis] +=  amount
        re_cali = "{\"y\": %f, \"z\": %f, \"x\": %f}" % (cali["y"],cali["z"],cali["x"])
        print(re_cali)

        calibrations["data"]["a:p10-8"]["calibration_data"]["C3"]["children"]["PCR-strip-tall"]["delta"] = re_cali
    with open("../robots/da5id_dup/calibrations/calibrations.json","w") as json_file:
        json.dump(calibrations,json_file,indent=4)

turret = "a"
pipette = "p10-8"
slot = "C3"
container = "PCR-strip-tall"
axis = "y"
amount = -1



change_calibration(turret,pipette,slot,container,axis,amount)




#
