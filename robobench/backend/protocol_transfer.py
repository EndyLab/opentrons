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
	# data for eppendorf pipette
	pos_dict =	{	
		'A1':{'96-flat':(23, 36, -50)},
		'B1':{'96-flat':(116, 36, -50)},
		'C1':{'96-flat':(208, 36, -50)},
		'D1':{'96-flat':(299, 36, -50)},
		'A2':{'96-flat':(23, 172, -50)},
		'B2':{'96-flat':(116, 172, -50)},
		'C2':{'96-flat':(208, 172, -50)},
		'D2':{'96-flat':(299, 172, -50)},
		'A3':{'96-flat':(23, 305, -50)},
		'B3':{'96-flat':(116, 305, -50)},
		'C3':{'96-flat':(208, 305, -50)},
		'D3':{'96-flat':(299, 305, -50)},
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
def transfer(pipette, source_data, dest_data, wells, vol):
	# source = calibrateToSlot(source_data['labware'], 'source', source_data['slot'], pipette)
	# dest = calibrateToSlot(dest_data['labware'], 'dest', dest_data['slot'], pipette)
	labwareDict = {
		'WellPlate': '96-flat',
	}
	source = calibrateToSlot(labwareDict[source_data['labware']], 'source', source_data['slot'], pipette)
	dest = calibrateToSlot(labwareDict[dest_data['labware']], 'dest', dest_data['slot'], pipette)

	# wells will be in form {source, dest}
	for key, value in wells.items(): 
		# aspirate from source
		pipette.aspirate(vol, source.wells(key))

		# dispense to dest
		pipette.dispense(dest.wells(value))


# connects to robot automatrically and homes it and instantiates pipette
def web_transfer(source_data, dest_data, vol):
	opentrons_connect()
	robot.home('xyzab')
	p200 = instruments.Pipette(axis='b', max_volume=200)
	# p200.calibrate_plunger(top=5, bottom=15, blow_out=15, drop_tip=15)
	# p200.update_calibrations()

	# make well dictionary
	wells = {}
	for source, dest in zip(source_data['wells'], dest_data['wells']):
		wells.update({source: dest})

	print(wells)

	transfer(p200, source_data, dest_data, wells, vol)

	#

def test_transfer():
	opentrons_connect()
	robot.home('xyzab')
	# calibrate stuff on the deck

	# tiprack = containers.load('tiprack-200ul', 'A1')
	# water = containers.load('point', 'A1', 'water')
	# plate_source = containers.load('96-flat', 'D1', 'plate')
	# plate_dest = containers.load('96-flat', 'D2', 'plate')
	p200 = instruments.Pipette(axis='b', max_volume=200)

	# given a slot, instantiate and calibrate a 96-well

	# p200.calibrate_plunger(top=12, bottom=20, blow_out=20, drop_tip=27)
	# p200.update_calibrations()

	wells = {
		'A1': 'B1',
		'A2': 'B2',
		'A3': 'B3',
	}
	source = {
		'labware': '96-flat', 
		'slot': 'C1', 
	} 
	dest = {
		'labware': '96-flat', 
		'slot': 'B1', 
	} 
	transfer(p200, source, dest, wells, 100)

	robot.disconnect()

def test_web_trasnfer():
	test_data =  {
            "protocol": "transfer",
            "volume": 10,
            "source": {
                "labware":"96-flat",
                "slot":"A1",
                "wells":["A1","A2","A3"]
            },
            "dest": { 
                "labware":"96-flat",
                "slot":"C2",
                "wells":["B1", "B2", "B3"]
            }
        }

	web_transfer(test_data['source'], test_data['dest'], test_data['volume'])

# if __name__ == '__main__':
# 	test_web_trasnfer()
