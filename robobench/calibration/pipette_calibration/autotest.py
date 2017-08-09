from snapshot import scale_to_digit, isolate_screen
import snapshot
import glob, os
import json
import cv2 

def list_to_str(vals):
	res = ''
	for val in vals:
		res = res + str(val)
	return res

img = cv2.imread("screen.png")
img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/screen" 
screen_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/crops"
# load screens
os.chdir(img_dir)

# load img digit key from json file
with open('key.json') as json_data:
	key = json.load(json_data)

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

os.chdir(screen_dir)

# now analyze the screen crops
for file in glob.glob("*.jpg"):
	print('opening ' + file)
	screen = cv2.imread(file)

	# find aspect ratios
	
# results 
print("num imgs:", str(num_imgs))
print("screen detected", str(success/num_imgs*100), '%')


