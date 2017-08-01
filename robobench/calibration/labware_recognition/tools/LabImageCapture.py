import cv2
import imutils
import re
import time
from os import listdir
from os.path import isfile, join
import sys

# Classes to train for
labware = ['96wellplate', 'tiprack', 'trough', 'scale', 'trash']
# Names of robots with grids
boxes = ['enzo', 'hiro']
# Names of robobenches
benches = ['yt']
# Grid positions
positions = ['A1', 'A2', 'A3',
			 'B1', 'B2', 'B3',
			 'C1', 'C2', 'C3',
			 'D1', 'D2', 'D3',
			 'E1', 'E2', 'E3']
# Files saved as labware_robot_pos_dataset-num.jpg
img_dir = '../models/object_detection/VOCdevkit/VOC2012/JPEGImages'
# Stores top left and bottom right to crop for
crop_points = []

def getLabwareType():
	labware_type = input("Labware type: ")
	while labware_type not in labware:
		print("Labware: " + str(labware))
		labware_type = input("Labware type: ")
	return labware_type

def getRobotName():
	robot_name = input("Robot name: ")
	while robot_name not in boxes and robot_name not in benches:
		print("Boxes: " + str(boxes))
		print("Benches: " + str(benches))
		robot_name = input("Robot name: ")
	return robot_name

def getDatasetName():
	d = input("Dataset ([t]rain or [v]alidate): ")
	while d != "train" and d != "validate" and d != "t" and d != "v":
		d = input("Dataset ([t]rain or [v]alidate):")
	if (d == "train"):
		d = "t"
	elif (d == "validate"):
		d = "v"
	return d

def getROI(event, x, y, flags, param):
	"""
	Mouse event handler
	Expects ROI drawn as rect from top left to bottom right
	Stores corner points in crop_points
	"""
    global crop_points

    if event == cv2.EVENT_LBUTTONDOWN:
        crop_points = [(x,y)]
    elif event == cv2.EVENT_LBUTTONUP:
        crop_points.append((x,y))

    print(crop_points)

def getIndex(prefix):
	"""
	Returns next available index for given image prefix (item_robot_pos_dataset) in img_dir
	"""
	filesInDir = [f.split('-')[1][:-4] for f in listdir(img_dir) if isfile(join(img_dir, f)) and f.startswith(prefix)]
	print(filesInDir)
	if len(filesInDir) == 0:
		print(filesInDir)
		return 0
	else:
		filesInDir.sort(key=lambda x: int(x), reverse=True)
		print(filesInDir)
		return int(filesInDir[0]) + 1

def setCrop(img):
	"""
	Opens window with passed in img and allows ROI to be drawn. Closes when key pressed
	"""
    cv2.namedWindow('Set crop')
    cv2.imshow('Set crop', img)
    cv2.setMouseCallback('Set crop', getROI)
    cv2.waitKey(0)
    print(crop_points)
    cv2.destroyWindow('Set crop')

def benchImageCapture(camera, labware_type, robot_name, dataset):
	"""
	Captures images with given parameters until 'n' is pressed
	Press 'c' to capture image
	Press 'n' to enter new settings
	Press 'q' to quit program
	"""
	prefix = labware_type + "_" + robot_name + "_deck_" + dataset
	while True:
		(grabbed, frame) = camera.read()
		frame = imutils.resize(frame, width=700)
		roi = cropFrame(frame)
		cv2.imshow("Video", roi)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("c"):
			index = getIndex(prefix)
			file = prefix + "-" + str(index) + ".jpg"
			print(file)
			path = join(img_dir, file)
			print(path)
			cv2.imwrite(path, roi)
		if key == ord("n"):
			return
		if key == ord("q"):
			sys.exit(0)

def cropFrame(frame):
	if len(crop_points) == 2:
		roi = frame[crop_points[0][1]:crop_points[1][1], crop_points[0][0]:crop_points[1][0]]
	else:
		roi = frame
	return roi

def boxImageCapture(camera, labware_type, robot_name, dataset):
	"""
	Captures one image for each deck position with given parameters
	Press 'c' to capture image
	Press 'n' to enter new settings
	Press 'q' to quit program
	"""
	global positions
	for pos in positions:
		print(pos)
		while True:
			prefix = labware_type + "_" + robot_name + "_" + pos + "_" + dataset 
			(grabbed, frame) = camera.read()
			frame = imutils.resize(frame, width=700)
			roi = cropFrame(frame)
			cv2.imshow("Video", roi)
			key = cv2.waitKey(1) & 0xFF
			if key == ord("c"):
				index = getIndex(prefix)
				file = prefix + "-" + str(index) + ".jpg"
				print(file)
				path = join(img_dir, file)
				print(path)
				cv2.imwrite(path, roi)
				break
			if key == ord("n"):
				return
			if key == ord("q"):
				sys.exit(0)


def collectImages():
	"""
	Continually gets parameters (object type, robot name, dataset) then captures images
	"""
	camera = cv2.VideoCapture(0)
	time.sleep(.25)
	while True:
		labware_type = getLabwareType()
		robot_name = getRobotName()
		dataset = getDatasetName()
		(grabbed, frame) = camera.read()
		frame = imutils.resize(frame, width=700)
		setCrop(frame)
		if robot_name in benches:
			benchImageCapture(camera, labware_type, robot_name, dataset)
		else:
			boxImageCapture(camera, labware_type, robot_name, dataset)


if __name__ == "__main__":
	collectImages()