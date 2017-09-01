import glob, os
import cv2
import json


img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/flat_camera/screen_train" 
# dict format: {'file name': digits}
key = {}

# load screens
os.chdir(img_dir)
test_imgs = []
count = 0
for file in glob.glob("*.jpg"):
	print('opening ' + file)
	screen = cv2.imread(file)
	test_imgs.append(screen)

	cv2.imshow('screen', screen)

	# add entry to dict with file name and digit
	# spam = input('spam')
	cv2.waitKey(2000)
	cv2.destroyAllWindows()
	digits = input('Enter digit for ' + str(file) + ':')
	print('you entered: ' + digits)
	key[str(file)] = digits
	count += 1
	print("num img labeled: ", count)

print("num imgs:", len(test_imgs))

with open('key.json', 'w+') as f:
	json.dump(key, f, indent=4)