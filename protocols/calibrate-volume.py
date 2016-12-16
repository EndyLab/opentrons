from opentrons import robot, containers, instruments

tiprack = containers.load('tiprack-200ul', 'B2')
plate = containers.load('96-flat', 'B1')
ddH2O = containers.load('point', 'B3', 'ddH2O-trough')
trash = containers.load('point', 'C2', 'holywastedplasticbatman')

p200 = instruments.Pipette(
    axis='a',
    max_volume=230,
    min_volume=20,
    tip_racks=[tiprack],
    trash_container=trash,
    channels=8,
    name='p200-8'
)

p200.pick_up_tip()

for well in plate.rows:
    p200.aspirate(225, ddH2O)
    p200.dispense(well)

p200.drop_tip()
