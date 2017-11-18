from opentrons import robot, containers, instruments

p10_tiprack = containers.load('tiprack-10ul', 'D2')
p200_tiprack = containers.load('tiprack-200ul', 'C3')
plate1 = containers.load('96-flat', 'C1')
plate2 = containers.load('96-flat', 'D1')
ddH2O = containers.load('point', 'A1', 'ddH2O-trough')
trash = containers.load('point', 'B2', 'holywastedplasticbatman')

p10 = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=[p10_tiprack],
    trash_container=trash,
    channels=8,
    name='p10-8'
)

p200 = instruments.Pipette(
    axis='b',
    max_volume=200,
    min_volume=20,
    tip_racks=[p200_tiprack],
    trash_container=trash,
    channels=1,
    name='p200-1'
)

p10.pick_up_tip()
for well in plate2.rows:
    p10.aspirate(9, ddH2O)
    p10.dispense(well.bottom())
    p10.blow_out()
    p10.touch_tip()

p10.drop_tip()

p200.pick_up_tip()

for well in plate1.rows:
    p200.aspirate(200, ddH2O)
    p200.blow_out(well.bottom())
    p200.touch_tip()

p200.drop_tip()
