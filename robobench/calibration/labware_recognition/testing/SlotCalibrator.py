import cv2
import imutils
import ObjectDetector
from PIL import Image
import time
import copy

positions = ['A1', 'A2', 'A3',
			 'B1', 'B2', 'B3',
			 'C1', 'C2', 'C3',
			 'D1', 'D2', 'D3',
			 'E1', 'E2', 'E3']
slot_points = []
crop_points = [(122, 15), (409, 247)]
slot_dict = {'D2': [(168, 89), (213, 157)], 'A3': [(36, 23), (79, 90)], 'D1': [(169, 157), (212, 223)], 
			'C3': [(125, 23), (170, 89)], 'A2': [(35, 91), (79, 156)], 'B3': [(79, 22), (124, 88)], 
			'D3': [(170, 23), (214, 89)], 'E1': [(214, 158), (258, 224)], 'C2': [(125, 89), (169, 157)], 
			'E3': [(215, 22), (259, 89)], 'B1': [(79, 155), (124, 222)], 'C1': [(124, 156), (169, 222)], 
			'B2': [(79, 91), (123, 155)], 'A1': [(35, 156), (79, 221)], 'E2': [(214, 90), (258, 157)]}

def setCrop(img):
	"""
	Opens window with passed in img and allows ROI to be drawn. Closes when key pressed
	"""
	cv2.namedWindow('Set crop')
	cv2.imshow('Set crop', img)
	cv2.setMouseCallback('Set crop', getROI, crop_points)
	cv2.waitKey(0)
	print(crop_points)
	cv2.destroyWindow('Set crop')

def setSlots(img):
	for pos in positions:
		windowName = 'Bound ' + pos
		cv2.namedWindow(windowName)
		cv2.imshow(windowName, img)
		cv2.setMouseCallback(windowName, getROI, slot_points)
		slot_points.clear()
		while len(slot_points) != 2:
			cv2.waitKey(0)
		slot_dict[pos] = copy.deepcopy(slot_points)
		print(slot_dict)

def getROI(event, x, y, flags, param):
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

def cropFrame(frame):
	if len(crop_points) == 2:
		roi = frame[crop_points[0][1]:crop_points[1][1], crop_points[0][0]:crop_points[1][0]]
	else:
		roi = frame
	return roi

def scaleBoxes(name_to_box_map, img_pil):
	width, height = img_pil.size
	for item in name_to_box_map.keys():
		box = name_to_box_map[item][0]
		name_to_box_map[item][0] = (box[0] * height, box[1] * width,
									box[2] * height, box[3] * width)
def determineSlot(box):
	middle = ((box[1] + box[3]) / 2, (box[0] + box[2]) / 2)
	# print('Middle: {}'.format(middle))
	for pos, slot_box in slot_dict.items():
		# print('Slot box: {}'.format(slot_box))
		if middle[0] > slot_box[0][0] and middle[0] < slot_box[1][0] and middle[1] > slot_box[0][1] and middle[1] < slot_box[1][1]:
			return pos
	return 'Undetermined location'

def evaluateDeck(img):
	print("Evaluate deck")
	img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	img_pil = Image.fromarray(img)
	obj_boxes = ObjectDetector.detectPIL(img_pil)
	width,height = img_pil.size
	scaleBoxes(obj_boxes, img_pil)
	# print(obj_boxes)
	for item, boxes in obj_boxes.items():
		box = boxes[0]
		slot = determineSlot(box)
		print('{} at {}'.format(item, slot))

if __name__ == "__main__":
	camera = cv2.VideoCapture(0)
	time.sleep(.25)
	(grabbed, frame) = camera.read()
	frame = imutils.resize(frame, width=500)
	# setCrop(frame)
	frame = cropFrame(frame)
	# setSlots(frame)
	while True:
		(grabbed, frame) = camera.read()

		frame = imutils.resize(frame, width=500)
		frame = cropFrame(frame)
		cv2.imshow("Video", frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("c"):
			evaluateDeck(frame)
		if key == ord("q"):				
			break



