from opentrons import robot, containers, instruments

tiprack = containers.load('tiprack-200ul', 'A1')
plate = containers.load('96-flat', 'B2')
ddH2O = containers.load('point', 'B3')
trash = containers.load('point', 'C3', 'holywastedplasticbatman')

p200 = instruments.Pipette(
    axis='b',
    max_volume=200,
    min_volume=20,
    tip_racks=[tiprack],
    trash_container=trash,
    channels=8,
    name='p200-8'
)

def move_liquid(start, end, volume):
    p200.pick_up_tip()
    p200.aspirate(volume, plate[start])
    p200.dispense(plate[end])
    p200.drop_tip()

    print(robot.commands())
    robot.simulate()

def dilution_series(dilution_frac=1e-1, num_tubes=5):
    robot.home(enqueue=True)

    volume = 200 # ul
    rows = plate.rows[:num_tubes]

    p200.pick_up_tip()
    for row in rows[1:]:
        p200.aspirate(volume * (1-dilution_frac), ddH2O)
        p200.dispense(row)
    p200.drop_tip()

    for source, dest in zip(rows, rows[1:]):
        p200.pick_up_tip()
        p200.mix(3, 200, source)
        p200.aspirate(volume * dilution_frac, source)
        p200.dispense(dest).blow_out().touch_tip()
        p200.drop_tip()

    print(robot.commands())
    robot.simulate()
