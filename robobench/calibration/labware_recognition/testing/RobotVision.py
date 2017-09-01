import cv2
import imutils
import ObjectDetector
import time
import copy
from opentrons import robot
from inspect import getsourcefile
from os.path import abspath

# get absolute path to this file so can be called from other directories
absolute_path = abspath(getsourcefile(lambda:0)) 
ckpt_path = absolute_path + "../models/object_detection/FineTune1/outputs/38385/frozen_inference_graph.pb"
label_path = absolute_path + "../models/object_detection/FineTune1/data/pascal_label_map_finetune1.pbtxt"
num_classes = 5
#num_classes = 7
skip = ['well', 'scale_screen']


# Hardcoded slot dict for defined camera position
slot_dict = {'B1': [(76, 156), (120, 223)], 'A3': [(31, 23), (75, 88)], 'C3': [(120, 23), (165, 90)], 
		'C2': [(120, 90), (166, 157)], 'E2': [(210, 90), (256, 157)], 'C1': [(121, 157), (167, 225)], 
		'D3': [(166, 22), (209, 89)], 'E1': [(211, 157), (256, 223)], 'D2': [(166, 90), (210, 158)], 
		'A2': [(31, 91), (76, 157)], 'A1': [(31, 158), (76, 224)], 'D1': [(166, 158), (212, 225)], 
		'B2': [(75, 91), (120, 157)], 'B3': [(77, 24), (120, 90)], 'E3': [(210, 23), (256, 90)]}
# top left and bottom right crop points for deck with defined camera position
crop_points = [(110, 37), (398, 274)]
positions = ['A1', 'A2', 'A3',
			 'B1', 'B2', 'B3',
			 'C1', 'C2', 'C3',
			 'D1', 'D2', 'D3',
			 'E1', 'E2', 'E3']

def cropFrame(frame):
	'''
	Returns cropped frame if there are two crop_points (top left and bottom right), otherwise
	returns frame
	'''
	if len(crop_points) == 2:
		roi = frame[crop_points[0][1]:crop_points[1][1], crop_points[0][0]:crop_points[1][0]]
	else:
		roi = frame
	return roi

def scaleBoxes(name_to_boxes_map, img):
	'''
	Scales box to pixels from normalized bounds
	'''
	height, width, _ = img.shape
	for name, boxes in name_to_boxes_map.items():
		for i in range(len(boxes)):
			box = boxes[i]
			name_to_boxes_map[name][i] = (box[0] * height, box[1] * width,
										box[2] * height, box[3] * width)
	

def determineSlot(box):
	'''
	Given box in format (ymin, xmin, ymax, xmax), determines slot using slot_dict
	slot_dict boxes are in positions are in format ((xmin, ymin), (xmax, ymax))
	'''
	middle = ((box[1] + box[3]) / 2, (box[0] + box[2]) / 2)
	for pos, slot_box in slot_dict.items():
		if middle[0] > slot_box[0][0] and middle[0] < slot_box[1][0] and middle[1] > slot_box[0][1] and middle[1] < slot_box[1][1]:
			return pos
	return 'Undetermined location'

def evaluateDeckSlots():
	'''
	Checks items on deck and returns dict of {slot:item type}
	Assumes that pipette is not occluding top camera
	'''

	camera = cv2.VideoCapture(0)
	time.sleep(.25)
	ret, frame = camera.read()
	frame = imutils.resize(frame, width=500)
	frame = cropFrame(frame)

	name_to_boxes_map = ObjectDetector.detectMat(frame, num_classes=num_classes, graph_path=ckpt_path, label_path=label_path)
	# print(name_to_boxes_map)
	scaleBoxes(name_to_boxes_map, frame)
	# print(name_to_boxes_map)
	slot_item_dict = {}
	for name, boxes in name_to_boxes_map.items():
		if name not in skip:
			for box in boxes:
				pos = determineSlot(box)
				slot_item_dict[pos] = name

	return slot_item_dict

if __name__ == "__main__":
	print(evaluateDeckSlots())

