from snapshot import scale_to_digit, isolate_screen
import snapshot
import glob, os
import json
import cv2 
import numpy as np

def list_to_str(vals):
	res = ''
	for val in vals:
		res = res + str(val)
	return res

def check_screen_extraction(dir):
	# load screens
	os.chdir(dir)

	# iterate through images
	num_imgs = 0
	failed = 0
	success = 0
	for file in glob.glob("*.jpg"):
		print('opening ' + file)
		screen = cv2.imread(file)

		# test screen extraction
		res = extracted_screen = snapshot.extract_screen(screen, file)
		if res == 0:
			success = success + 1

		num_imgs = num_imgs+1

	# results 
	print("num imgs:", str(num_imgs))
	print("screen detected", str(success/num_imgs*100), '%')

def get_screen_info(dir):
	os.chdir(dir)

	total_h = 0
	total_w = 0
	count = 0
	for file in glob.glob('*.jpg'):
		print('opening'+file)
		crop = cv2.imread(file)

		# get screen dimensions
		h, w = crop.shape[:2]
		total_h = total_h + h
		total_w = total_w + w
		# print(w, h)

		count = count + 1

	return total_w//count, total_h//count

def normalize_screens(dir, aspect_ratio):
	os.chdir(dir)
	for file in glob.glob('*.jpg'):
		img = cv2.imread(file)

		# resize image
		resize_w = 100
		resize_h = int(resize_w * float(1/aspect_ratio))

		resized = cv2.resize(img, (resize_w, resize_h), interpolation = cv2.INTER_AREA)
		# cv2.imshow("resized", resized)
		# cv2.waitKey(0)

		# write to new folder
		cv2.imwrite(r"C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms/"+file, resized)

img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/screen" 
screen_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/crops"
normed_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms"
# load img digit key from json file
os.chdir(img_dir)
with open('key.json') as json_data:
	key = json.load(json_data)

# check_screen_extraction(img_dir)
w, h = get_screen_info(screen_dir)
aspect = float(w/h)
print(aspect)

normalize_screens(screen_dir, aspect)





