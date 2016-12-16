from opentrons import robot, containers, instruments
# from opentrons_sdk.helpers.helpers import import_calibration_json

PORT = '/dev/tty.usbmodem621'

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

robot.connect(PORT)
robot.home()
#
# with open('./calibrations/calibrations.json', 'r') as c:
#     import_calibration_json(c, robot, True)

def move_liquid(start, end, volume):
    # robot.home(enqueue=True)
    robot.clear_commands()

    p200.pick_up_tip()
    p200.aspirate(volume, plate[start])
    p200.dispense(volume, plate[end])
    p200.drop_tip()

    print(robot.commands())
    robot.run()
    robot.clear_commands()

def dilution_series(dilution_frac=1e-1, num_tubes=5):
    robot.clear_commands()

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
    robot.run()
    robot.clear_commands()
