from opentrons import robot, containers, instruments

p10_tiprack = containers.load('tiprack-10ul', 'D2')
p200_tiprack = containers.load('tiprack-200ul', 'C3')

tubes = containers.load('96-PCR-tall','C1')
strip = containers.load('PCR-strip-tall','D1')

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

p10.aspirate(9, strip['A1'].bottom())
p10.dispense(tubes.wells('A1').bottom())

p10.aspirate(9, strip['A1'].bottom())
p10.dispense(tubes.wells('A2').bottom())

p10.return_tip()

robot.reset()

p10single_tiprack = containers.load('tiprack-10ul','E3')

tubes = containers.load('96-PCR-tall','C1')
strip = containers.load('PCR-strip-tall','D1')
ddH2O = containers.load('point', 'A1', 'ddH2O-trough')
trash = containers.load('point', 'B2', 'holywastedplasticbatman')

tubes = containers.load('96-PCR-tall','C1')
strip = containers.load('PCR-strip-tall','D1')

p10single = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=[p10single_tiprack],
    trash_container=trash,
    channels=1,
    name='p10-8s'
)


p10single.pick_up_tip()

p10single.aspirate(9, strip['A1'].bottom())
p10single.dispense(tubes.wells('D1').bottom())

p10single.return_tip()

