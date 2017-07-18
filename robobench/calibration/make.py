import cv2
from matplotlib import pyplot as plt
import dipdigits
import glob, os
import sys


program_name = sys.argv[0]
arguments = sys.argv[1:]
count = len(arguments)
debug = 'off'
if count >= 1:
	# debug toggle
	if arguments[0] == '-d':
		debug = 'on'


img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/test" 
new_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/processed" 
gray_dir = "C:/Users/gohna/Downloads/birme"
ratio = 0.2

"""
os.chdir(gray_dir)
for file in glob.glob("*.jpg"):
	# if "IMG_20170714_224142" in file:
	print(file)
	img = cv2.imread(file)
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	cv2.imwrite(file,img_gray)
	# img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
	# crop: assume screen is in bottom half of picture
	# h, w, channels = img_scaled.shape 
	# crop_img = img_scaled[h//2:h, 0:w]
	# cv2.imshow("orig cropped", crop_img)
	# test_imgs.append(crop_img)

"""
# load test imgs
os.chdir(img_dir)
test_imgs = []
if os.path.exists(img_dir):
    os.chdir(img_dir)
    for file in glob.glob("*.jpg"):
    	# if "IMG_20170714_224142" in file:
    	img = cv2.imread(file)
    	img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
    	# crop: assume screen is in bottom half of picture
    	h, w, channels = img_scaled.shape 
    	crop_img = img_scaled[h//2:h, 0:w]
    	# cv2.imshow("orig cropped", crop_img)
    	test_imgs.append(crop_img)
 
print("num imgs:", len(test_imgs))
# process imgs
os.chdir(new_dir)
file = open("C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/test.txt","w") 
count = 1
for i, img in enumerate(test_imgs):
	# if i != 2:
	# 	continue;
	name = "screen"+str(i)+".jpg"
	pts = dipdigits.find_screen(img, debug)
	tl_pt = dipdigits.find_top_left_point(pts)
	print("points:",pts,"top left:",tl_pt)

	screen = dipdigits.crop_screen(img, pts)
	h, w, channels = screen.shape 
	pixel= screen[h//2, w//2]
	print("pixel at center of screen:",pixel)
	line = str(pixel[0]) + " " + str(pixel[1]) + " " + str(pixel[2]) + "\n"
	file.write(line)
	cv2.imshow("screen cropped", screen)
	cv2.imwrite(name,screen)
	print(count)
	count = count+1
	
file.close() 

cv2.waitKey(0)
cv2.destroyAllWindows()
