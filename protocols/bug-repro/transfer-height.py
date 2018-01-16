from opentrons import robot, containers, instruments

p10_tipracks = [containers.load('tiprack-10ul', 'E2')]
p200_tipracks = [containers.load('tiprack-200ul', 'A3')]
pcr = containers.load('96-PCR-tall', 'C2')
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

# p200.transfer(1, pcr.wells('A1'), pcr.wells('A2'), touch_tip=True, new_tip="always", blow_out=True)

robot.arc_height=20
p10.transfer(1, pcr.rows('1'), pcr.rows('2'), touch_tip=True, new_tip="always", blow_out=True)

for c in robot.commands():
    print(c)
