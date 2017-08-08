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
screen_failed = 0
screen_success = 0
for file in glob.glob("*.jpg"):
	print('opening ' + file)
	screen = cv2.imread(file)
	# cv2.imshow('screen', screen)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	
	# res = snapshot.color_filter(screen)
	# res = isolate_screen(screen)

	extracted_screen = snapshot.extract_screen(screen, file)
	
	# os.chdir(screen_dir)
	# if extracted_screen != -1:
		# cv2.imshow('cropped', extracted_screen)

	# if res != [-1, -1, -1, -1]:
		# screen_success = screen_success + 1



	# res = scale_to_digit(screen, debug='off')

	# if res == -1:
	# 	screen_failed = screen_failed+1
	# else:
	# 	num = list_to_str(res)
	# 	print('result: ', num, 'actual: ', key[file])
	# 	if num == key[file]:
	# 		print('YAY')

	num_imgs = num_imgs+1


print("num imgs:", str(num_imgs))
print("screen detected", str((screen_success)/num_imgs*100), '%')


