from opentrons import robot, instruments, containers

tiprack = containers.load('tiprack-200ul', 'A1')
water = containers.load('point', 'A1', 'water')
scale = containers.load('point', 'A1', 'scale')
scale_screen = containers.load('point', 'A1', 'screen')
p200 = instruments.Pipette(axis='b', max_volume=200)

p200.pick_up_tip(tiprack[0])
p200.pick_up_tip(water[0])
p200.pick_up_tip(scale[0])
p200.pick_up_tip(scale_screen[0])
