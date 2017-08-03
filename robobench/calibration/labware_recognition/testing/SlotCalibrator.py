import cv2
import imutils
import ObjectDetector
from PIL import Image
import time
import copy
from opentrons import robot, instruments, containers

class SlotCalibrator:
	positions = ['A1', 'A2', 'A3',
			 'B1', 'B2', 'B3',
			 'C1', 'C2', 'C3',
			 'D1', 'D2', 'D3',
			 'E1', 'E2', 'E3']
	slot_points = []
	crop_points = [(122, 15), (409, 247)]
	slot_bounding_dict = {'D2': [(168, 89), (213, 157)], 'A3': [(36, 23), (79, 90)], 'D1': [(169, 157), (212, 223)], 
			'C3': [(125, 23), (170, 89)], 'A2': [(35, 91), (79, 156)], 'B3': [(79, 22), (124, 88)], 
			'D3': [(170, 23), (214, 89)], 'E1': [(214, 158), (258, 224)], 'C2': [(125, 89), (169, 157)], 
			'E3': [(215, 22), (259, 89)], 'B1': [(79, 155), (124, 222)], 'C1': [(124, 156), (169, 222)], 
			'B2': [(79, 91), (123, 155)], 'A1': [(35, 156), (79, 221)], 'E2': [(214, 90), (258, 157)]}
	# Next step is achieving fine precision automatically
	# Hardcoding for now, could probably be good enough by looking at dx/dy
	# add points
	# pos_dict = {'A1':{'tiprack-200ul':(33, 35.5, -33), '96-flat':(34, 35.5, -45)},
	# 			'B1':{'tiprack-200ul':(125, 35.5, -33), '96-flat':(126, 35.5, -45)},
	# 			'C1':{'tiprack-200ul':(216.5, 35.5, -33), '96-flat':(217.5, 35.5, -45)},
	# 			'D1':{'tiprack-200ul':(308.5, 35.5, -33), '96-flat':(309.5, 35.5, -45)},
	# 			'A2':{'tiprack-200ul':(33, 171.5, -33), '96-flat':(34, 171.5, -45)},
	# 			'B2':{'tiprack-200ul':(125, 171.5, -33), '96-flat':(126, 171.5, -45)},
	# 			'C2':{'tiprack-200ul':(216.5, 171.5, -33), '96-flat':(217.5, 171.5, -45)},
	# 			'D2':{'tiprack-200ul':(308.5, 171.5, -33), '96-flat':(309.5, 171.5, -45)},
	# 			'A3':{'tiprack-200ul':(33, 304.5, -33), '96-flat':(34, 304.5, -45)},
	# 			'B3':{'tiprack-200ul':(125, 304.5, -33), '96-flat':(126, 304.5, -45)},
	# 			'C3':{'tiprack-200ul':(216.5, 304.5, -33), '96-flat':(217.5, 304.5, -45)},
	# 			'D3':{'tiprack-200ul':(308.5, 304.5, -33), '96-flat':(309.5, 304.5, -45)},
	pos_dict = {'A1':{'tiprack-200ul':(33, 35.5, -33)},
			'B1':{'tiprack-200ul':(125, 35.5, -33)},
			'C1':{'tiprack-200ul':(216.5, 35.5, -33)},
			'D1':{'tiprack-200ul':(308.5, 35.5, -33)},
			'A2':{'tiprack-200ul':(33, 171.5, -33)},
			'B2':{'tiprack-200ul':(125, 171.5, -33)},
			'C2':{'tiprack-200ul':(216.5, 171.5, -33)},
			'D2':{'tiprack-200ul':(308.5, 171.5, -33)},
			'A3':{'tiprack-200ul':(33, 304.5, -33)},
			'B3':{'tiprack-200ul':(125, 304.5, -33)},
			'C3':{'tiprack-200ul':(216.5, 304.5, -33)},
			'D3':{'tiprack-200ul':(308.5, 304.5, -33)},
			}
	point_types = ['scale', 'trough', 'trash']

	def initialize(self):
		camera = cv2.VideoCapture(0)
		time.sleep(.25)
		grabbed, frame = camera.read()
		frame = imutils.resize(frame, width=500)
		self.setCrop(frame)
		frame = self.cropFrame(frame)
		self.generatePosDict()
		# self.setSlots(frame)

	def generatePosDict(self):
		for slot, item_pos_map in self.pos_dict.items():
			base_x, base_y, base_z = item_pos_map['tiprack-200ul']
			item_pos_map['96-flat'] = (base_x + 1, base_y, -45)
			item_pos_map['scale'] = (base_x + 35, base_y + 71.5, -23)
			item_pos_map['trough'] = (base_x + 32, base_y + 50.5, -36)
			item_pos_map['trash'] = (base_x + 32, base_y + 50.5, 9)

	def calibrate(self, instrument, items):
		"""
		Input: Dictionary of {name:labware type}
		Output: Dictionary of {name:OT object}, error if not all OT objects are found
		"""
		camera = cv2.VideoCapture(0)
		time.sleep(.25)
		grabbed, frame = camera.read()
		frame = imutils.resize(frame, width=500)
		frame = self.cropFrame(frame)
		item_slot_dict = self.evaluateDeck(frame)
		print(item_slot_dict)
		container_dict = {}
		for name, item in items.items():
			print('Name: {}'.format(name))
			print('Item: {}'.format(item))
			try:
				slot = item_slot_dict[item]
				print(slot)
				container = self.calibrateToSlot(item, name, slot, instrument)
				print('Calibrated to slot')
				container_dict[name] = container
			except KeyError:
				return {'error':'Item missing: {}'.format(item)}
		return container_dict

	def calibrateToSlot(self, item_type, name, slot, instrument):
		if item_type in self.point_types:
			ot_type = 'point'
		else:
			ot_type = item_type
		curr_container = containers.load(ot_type, slot, name)
		print(curr_container)
		rel_pos = curr_container[0].from_center(x=0, y=0, z=-1, reference=curr_container)
		print(rel_pos)
		print(self.pos_dict[slot][item_type])
		instrument.calibrate_position((curr_container, rel_pos), self.pos_dict[slot][item_type])
		return curr_container

	def evaluateDeck(self, frame):
		print("Evaluate deck")
		img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		img_pil = Image.fromarray(img)
		obj_boxes = ObjectDetector.detectPIL(img_pil)
		width,height = img_pil.size
		self.scaleBoxes(obj_boxes, img_pil)
		print(obj_boxes)
		item_slot_dict = {}
		for item, boxes in obj_boxes.items():
			box = boxes[0]
			slot = self.determineSlot(box)
			item_slot_dict[item] = slot
			print('{} at {}'.format(item, slot))
		return item_slot_dict

	def determineSlot(self, box):
		middle = ((box[1] + box[3]) / 2, (box[0] + box[2]) / 2)
		# print('Middle: {}'.format(middle))
		for pos, slot_box in self.slot_bounding_dict.items():
			# print('Slot box: {}'.format(slot_box))
			if middle[0] > slot_box[0][0] and middle[0] < slot_box[1][0] and middle[1] > slot_box[0][1] and middle[1] < slot_box[1][1]:
				return pos
		return 'Undetermined location'

	def scaleBoxes(self, name_to_box_map, img_pil):
		width, height = img_pil.size
		for item in name_to_box_map.keys():
			box = name_to_box_map[item][0]
			name_to_box_map[item][0] = (box[0] * height, box[1] * width,
										box[2] * height, box[3] * width)


	def setCrop(self, frame):
		"""
		Opens window with passed in img and allows ROI to be drawn. Closes when key pressed
		"""
		cv2.namedWindow('Set crop')
		cv2.imshow('Set crop', frame)
		cv2.setMouseCallback('Set crop', self.getROI, self.crop_points)
		cv2.waitKey(0)
		print(self.crop_points)
		cv2.destroyWindow('Set crop')

	def setSlots(self, img):
		for pos in self.positions:
			windowName = 'Bound ' + pos
			cv2.namedWindow(windowName)
			cv2.imshow(windowName, img)
			cv2.setMouseCallback(windowName, self.getROI, self.slot_points)
			self.slot_points.clear()
			while len(self.slot_points) != 2:
				cv2.waitKey(0)
			self.slot_bounding_dict[pos] = copy.deepcopy(self.slot_points)
			print(self.slot_bounding_dict)
			cv2.destroyWindow(windowName)

	def getROI(self, event, x, y, flags, param):
		"""
		Mouse event handler
		Expects ROI drawn as rect from top left to bottom right
		Stores corner points in crop_points
		"""

		if event == cv2.EVENT_LBUTTONDOWN:
			param.clear()
			param.append((x,y))
			print('down')
		elif event == cv2.EVENT_LBUTTONUP:
			param.append((x,y))
			print('up')

		print(param)

	def cropFrame(self, frame):
		if len(self.crop_points) == 2:
			roi = frame[self.crop_points[0][1]:self.crop_points[1][1], self.crop_points[0][0]:self.crop_points[1][0]]
		else:
			roi = frame
		return roi