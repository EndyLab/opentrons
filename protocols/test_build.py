from opentrons import robot, containers, instruments
import argparse
import sys

from datetime import datetime

# Specify locations, note that locations are indexed by the spot in the array
locations = np.array([["tiprack-200", "A3"],
                    ["tiprack-10", "E2"],
                    ["tiprack-10s1", "E3"],
                    ["tiprack-10s2", "E1"],
                    ["trash", "D1"],
                    ["PCR-strip-tall", "C3"],
                    ["DEST_PLATE", "C2"],
                    ["Tube Rack","B1"]])

# Attach a location to each of the source plates
layout = list(zip(pd.unique(plates),SOURCE_SLOTS[:len(plates)]))
locations = np.append(locations,layout, axis=0)

# Fill in the data frame with the locations
for row,col in locations:
    layout_table.loc[col[1], col[0]] = row

# Displays the required plate map and waits to proceed
#print()
#print("Please arrange the plates in the following configuration:")
#print()
#print(layout_table)
#print()

# Make the dataframe to represent the OT-1 deck
deck = ['A1','B2','C3','D2','E1']
slots = pd.Series(deck)
columns = sorted(slots.str[0].unique())
rows = sorted(slots.str[1].unique(), reverse=True)
layout_table = pd.DataFrame(index=rows, columns=columns)
layout_table.fillna("---", inplace=True)

robot.home()

p200_tipracks = [
    containers.load('tiprack-200ul', locations[0,1]),
]

p10_tipracks = [
    containers.load('tiprack-10ul', locations[1,1]),
]

trash = containers.load('point', locations[4,1], 'holywastedplasticbatman')
centrifuge_tube = containers.load('tube-rack-2ml',locations[7,1])
master = containers.load('PCR-strip-tall', locations[5,1])

dest_plate = containers.load('96-PCR-tall', locations[6,1])

source_plates = [
    containers.load('96-flat', "D2")
    containers.load('96-flat', "D3")
    containers.load('96-flat', "B2")
]

p10 = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=p10_tipracks,
    trash_container=trash,
    channels=8,
    name='p10-8',
    aspirate_speed=200,
    dispense_speed=600
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

start = datetime.now()
print("Starting run at: ",start)

p10.pick_up_tip()
for number in [0,1]:
    p10.transfer(8, master['A1'].bottom(), dest_plate.rows(1), mix_before=(1,8), blow_out=True, new_tip='never')
p10.drop_tip()

stop = datetime.now()
print(stop)
runtime = stop - start
print("Total runtime is: ", runtime)

p10 = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=p10_tipracks,
    trash_container=trash,
    channels=8,
    name='p10-8',
    aspirate_speed=400,
    dispense_speed=800
)

start = datetime.now()
print("Starting run at: ",start)

p10.pick_up_tip()
for number in [0,1]:
    p10.transfer(8, master['A1'].bottom(), dest_plate.rows(1), mix_before=(1,8), blow_out=True, new_tip='never')
p10.drop_tip()

stop = datetime.now()
print(stop)
runtime = stop - start
print("Total runtime is: ", runtime)
