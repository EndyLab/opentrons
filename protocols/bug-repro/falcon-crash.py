from opentrons import robot, containers, instruments

p10_tipracks = [containers.load('tiprack-10ul', 'E2')]
p200_tipracks = [containers.load('tiprack-200ul', 'A3')]
falcon = containers.load('tube-rack-15_50ml', 'A1')
trash = containers.load('point', 'D1', 'holywastedplasticbatman')

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

# robot.arc_height=20
p200.pick_up_tip()
p200.aspirate(100, falcon['A1'])

for c in robot.commands():
    print(c)
