import time
import cv2
import imutils
import re
import numpy as np
from os import listdir
from os.path import isfile, join
from opentrons import robot, instruments, containers


deck_ref_points = [(31.85,396.0), (362.65, 112.0)]
img_points = []
def build_reference(event, x, y, flags, param):
	global img_points
	if event == cv2.EVENT_LBUTTONUP:
		if (len(img_points) > 1):
			img_points.pop(0)
		img_points.append((x,y))
		print(img_points)

def transform(point, dim):
	global deck_ref_points, img_points
	return (point - img_points[0][dim]) / (img_points[1][dim] - img_points[0][dim]) * (deck_ref_points[1][dim] - deck_ref_points[0][dim]) + deck_ref_points[0][dim]

def move_robot(event, x, y, flags, param):
	global deck_ref_points, img_points
	if event == cv2.EVENT_LBUTTONUP:
		rx = transform(x, 0)
		ry = transform(y,1)
		print("Robot: {}, {}".format(rx, ry))
		robot.move_head(x=rx, y=ry)

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
    pipette = instruments.Pipette(axis='b')

cv2.namedWindow("Video")
cv2.setMouseCallback("Video", build_reference)

camera = cv2.VideoCapture(0)
opentrons_connect()
time.sleep(.25)

while True:
	(grabbed, frame) = camera.read()
	frame = imutils.resize(frame, width=500)
	cv2.imshow("Video", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("m"):
		print("Move mode")
		cv2.setMouseCallback("Video", move_robot)
	if key == ord("r"):
		print("Reference mode")
		cv2.setMouseCallback("Video", build_reference)
	if key == ord("h"):
		robot.home(now=True)

	if key == ord("q"):
		break

camera.release()
cv2.destroyAllWindows()


# def build_rectangle(event, x, y, flags, param):
# 	global points
# 	if event == cv2.EVENT_LBUTTONUP:
# 		if len(points) < 4:
# 			points.append((x,y))
# 		else:
# 			points = [(x,y)]
# 		print(points)