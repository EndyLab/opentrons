import argparse
import time
import cv2
import imutils
import re
from os import listdir
from os.path import isfile, join

parser = argparse.ArgumentParser()

category = parser.add_mutually_exclusive_group()
category.add_argument("-t", "--train", action="store_true")
category.add_argument("-v", "--validate", action="store_true")
parser.add_argument("-p", "--path")

args = parser.parse_args()

if args.validate:
	print("Validate")
	prefix = "valimage"
elif args.train:
	print("Train")
	prefix = "trainimage"
else:
	parser.error('Must specify --train or --validate')

if args.path:
	directory = args.path
else:
	directory = '../models/object_detection/VOCdevkit/VOC2012/JPEGImages'

def getIndex(filename):
	return int(''.join(list(filter(str.isdigit, filename))))

camera = cv2.VideoCapture(0)
time.sleep(.25)

index = 0
regex = re.escape(prefix) + r'[0-9]*.jpg'
filesInDir = [f for f in listdir(directory) if isfile(join(directory, f)) and re.match(regex, f)]
filesInDir.sort(key=lambda x: getIndex(x), reverse=True)
print(filesInDir)

if len(filesInDir) != 0:
	index = getIndex(filesInDir[0]) + 1
	print(index)
record = False

while True:
	(grabbed, frame) = camera.read()
	frame = imutils.resize(frame, width=500)
	cv2.imshow("Video", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("c") or record:
		file = prefix + str(index) + ".jpg"
		path = join(directory, file)
		cv2.imwrite(path, frame)
		if record:
			time.sleep(.5)
		index = index + 1
		print(path)
	if key == ord("r"):
		record = not record
	if key == ord("q"):
		break

camera.release()
cv2.destroyAllWindows()


