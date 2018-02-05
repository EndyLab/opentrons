from opentrons import robot, containers, instruments

port = robot.get_serial_ports_list()[0]
print("Connecting robot to port {}".format(port))
robot.connect(port)

robot.home()

p10_tiprack_single = containers.load('tiprack-10ul', 'E1')
p200_tiprack = containers.load('tiprack-200ul', 'A3')

centrifuge_tube = containers.load('tube-rack-2ml','B1')
tubes_single = containers.load('96-PCR-tall','C2')
strip_single = containers.load('PCR-strip-tall','C3')
source1_single = containers.load('96-flat','D2')
source3_single = containers.load('96-flat','D3')

trash = containers.load('point', 'D1', 'holywastedplasticbatman')

p10single = instruments.Pipette(
    axis='a',
    max_volume=10,
    min_volume=0.5,
    tip_racks=[p10_tiprack_single],
    trash_container=trash,
    channels=1,
    name='p10-8s'
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

p10single.pick_up_tip()

for well in range(95):
    print(well)
    #p10single.pick_up_tip()
    p10single.move_to(source1_single.wells(well).bottom())
    #p10single.drop_tip()
p10single.drop_tip()







