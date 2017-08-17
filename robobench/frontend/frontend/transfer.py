from opentrons import robot, instruments, containers

def opentrons_connect():
    try:
        # physical robot
        ports = robot.get_serial_ports_list()
        print(ports)
        robot.connect(ports[0])
    except IndexError:
        # simulator
        robot.connect('Virtual Smoothie')
        robot.home(now=True)

def get_coords():
    Point = []
    curr_coords = robot._driver.get_head_position()
    curr_x = curr_coords['current'].coordinates.x
    curr_y = curr_coords['current'].coordinates.y
    curr_z = curr_coords['current'].coordinates.z
    pos = [curr_x, curr_y, curr_z]
    # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
    return pos

def calibrateToSlot(item_type, name, slot, instrument):
	pos_dict =	{	
		'A1':{'96-flat':(33, 35.5, -33)},
		'B1':{'96-flat':(125, 35.5, -33)},
		'C1':{'96-flat':(216.5, 35.5, -33)},
		'D1':{'96-flat':(308.5, 35.5, -33)},
		'A2':{'96-flat':(33, 171.5, -33)},
		'B2':{'96-flat':(125, 171.5, -33)},
		'C2':{'96-flat':(216.5, 171.5, -33)},
		'D2':{'96-flat':(308.5, 171.5, -33)},
		'A3':{'96-flat':(33, 304.5, -33)},
		'B3':{'96-flat':(125, 304.5, -33)},
		'C3':{'96-flat':(216.5, 304.5, -33)},
		'D3':{'96-flat':(308.5, 304.5, -33)},
	}

	point_types = ['scale', 'trough', 'trash']
	if item_type in point_types:
		ot_type = 'point'
	else:
		ot_type = item_type
	curr_container = containers.load(ot_type, slot, name)
	# print(curr_container)
	rel_pos = curr_container[0].from_center(x=0, y=0, z=-1, reference=curr_container)
	# print(rel_pos)
	# print(pos_dict[slot][item_type])
	instrument.calibrate_position((curr_container, rel_pos), pos_dict[slot][item_type])
	return curr_container

"""
	Usage:
	----------------
	pipette: the pipette that transfers liquid
	source: tuple of source container type and slot Ex: () well, A1 )
	dest: destination plate
	wells: dictionary of wells to transfer stuff to asusming 1:1 well transfer ratio here
	vol: volume to transfer (1 volume for now MVP)
	96-flate the pipette gets its tips from
	water: where the water is 
"""
def transfer(pipette, source_dict, dest_dict, wells, vol):
	source = calibrateToSlot(source_dict[0], 'source', source_dict[1], pipette)
	dest = calibrateToSlot(dest_dict[0], 'dest', dest_dict[1], pipette)

	# wells will be in form {source, dest}
	for key, value in wells.items(): 
		# aspirate from source
		pipette.aspirate(vol, source.wells(key))

		# dispense to dest
		pipette.dispense(dest.wells(value))


if __name__ == '__main__':
	opentrons_connect()
	robot.home('xyzab')
	# calibrate stuff on the deck

	tiprack = containers.load('tiprack-200ul', 'A1')
	water = containers.load('point', 'A1', 'water')
	# plate_source = containers.load('96-flat', 'D1', 'plate')
	# plate_dest = containers.load('96-flat', 'D2', 'plate')
	p200 = instruments.Pipette(axis='b', max_volume=200)

	# given a slot, instantiate and calibrate a 96-well

	p200.calibrate_plunger(top=12, bottom=27, blow_out=33, drop_tip=34)
	p200.update_calibrations()

	wells = {
		'A1': 'B1',
		'A2': 'B2',
		'A3': 'B3'
	}
	source = ( '96-flat', 'D1' )
	dest = ( '96-flat', 'C2' )
	transfer(p200, source, dest, wells, 100)


	robot.disconnect()