import cv2
import dipdigits
import glob, os
from PIL import Image
import sys
from skimage import exposure
import numpy as np
from matplotlib import pyplot as plt



program_name = sys.argv[0]
arguments = sys.argv[1:]
count = len(arguments)
debug = 'off'
if count >= 1:
	# debug toggle
	if arguments[0] == '-d':
		debug = 'on'


img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/processed" 
new_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/processed" 

# load screens
os.chdir(img_dir)
test_imgs = []
for file in glob.glob("*.jpg"):
	if "screen14" in file:
		print(file)
		test_imgs.append(cv2.imread(file))
 
print("num imgs:", len(test_imgs))

# process screens
os.chdir(new_dir)
count = 1
for i, img in enumerate(test_imgs):
	# if i != 0:
	# 	continue;

	name = "digits"+str(i)+".jpg"
	
	# create a CLAHE object (Arguments are optional)
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img2 = exposure.rescale_intensity(img_gray, out_range = (0, 255))
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	cl1 = clahe.apply(img2)
	cv2.imwrite("clay a"+str(i)+".jpg",cl1)

	# thresholds
	adapt_thresh = cv2.adaptiveThreshold(img_gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
	cv2.imwrite("adapt"+str(i)+".jpg", adapt_thresh)

	h, w = adapt_thresh.shape[:2]
	print(h,w)
	mat = np.ones((3,3),np.uint8)
	# (h,w)
	compressed_mat = np.zeros((h//3, w//3))
	for x in range(0,w-3,3):
		for y in range(0,h-3,3):
			val = np.zeros((3, 3))
			# construct 3x3 matrix of pixel values
			crop = adapt_thresh[y:y+3,x:x+3]
			res = np.bitwise_and(mat,crop)
			nonzero = np.count_nonzero(res)
			if nonzero > 5:
				# white
				compressed_mat[y//3][x//3] = 255
			else:
				# blacki
				compressed_mat[y//3][x//3] = 0

	# im = Image.fromarray(compressed_mat)
	# im.save("your_file.jpeg")
	cv2.imwrite("compresed"+str(i)+".jpg", compressed_mat)

	# sliding window
	# h_comp, w_comp = compressed_mat.shape[:2]
	# digit_w = .15*w_comp
	# digit_h = h_comp
	# padding = 1
	# next_digit_x = 0
	# print("small:",h_comp,w_comp)
	# print("digit width:", digit_w)
	# for x in range(w_comp):
	# 	if x+digit_w < w_comp:
	# 		# print("y:", digit_h,"x:",x)
	# 		crop = compressed_mat[1:int(digit_h),x:int(x+digit_w)]
	# 		nonzero = np.count_nonzero(crop)
	# 		total_pixls = crop.size
	# 		# only save crop if num of white pixels is greater than 10%
	# 		# print("corops"+str(x)+str(i)+":", float(nonzero/total_pixls))
	# 		if float(nonzero/total_pixls) >= .10:
	# 			# first digit
	# 			next_digit_x = x+digit_w+padding
	# 			leftmost_x = x
	# 			cv2.imwrite("corops"+str(x)+str(i)+".jpg", crop)
	# 			break
	# 		else:
	# 			continue

	# given first digit slide over to get the next digits
	# while next_digit_x+digit_w < w_comp:
	# 	print("next digit:", next_digit_x)
	# 	crop = compressed_mat[1:int(digit_h),int(next_digit_x):int(next_digit_x+digit_w)]
	# 	nonzero = np.count_nonzero(crop)
	# 	total_pixls = crop.size
	# 	# only save crop if num of white pixels is greater than 10%
	# 	print("corops"+str(next_digit_x+digit_w)+str(i)+":", float(nonzero/total_pixls))
	# 	if float(nonzero/total_pixls) >= .10:
	# 		# next digit
	# 		cv2.imwrite("corops"+str(next_digit_x)+str(i)+".jpg", crop)
	# 	next_digit_x = next_digit_x+digit_w

	# print("left", leftmost_x)
	# crop = compressed_mat[0:,int(leftmost_x):]
	crop = compressed_mat.copy()
	cv2.imshow("asd",crop)
	h, w = crop.shape[:2]
	print(h,w)

	# build skeletonsof the segments joining horizontal contours
	# blank black slate
	skel = np.zeros((h, w))
	# hori = 255*np.ones((1, w))
	# vert = 255*np.ones((h,1))
	x = 0
	v_endpoints = []
	h_endpoints = []
	for y in range(h):
		while x < w:
			# if pixel is white
			if crop[y][x] == 255:
				# keep going until we reach black -> end of edge
				count=0
				start_x = x
				while crop[y][x] == 255 and x < w:
					count = count+1
					x = x+1
				if count >= 3:
					h_endpoints.append([(start_x,y),(x,y)])
					# endpoints.append((start_x,y))
					skel[y][start_x:x] = 255

			x=x+1
		x=0

	# vertical filter
	y = 0
	for x in range(w):
		while y < h:
			# if pixel is white
			if crop[y][x] == 255:
				# keep going until we reach black -> end of edge
				count=0
				start_y = y
				while crop[y][x] == 255 and y < h:
					count = count+1
					y = y+1
				if count >= 5:
					print(start_y,y)
					v_endpoints.append([(x,start_y),(x,y)])
					# endpoints.append((x,y))
					for j in range(start_y,y):
						skel[j][x] = 255
			y=y+1
		y=0

	cv2.imwrite("skele_all.jpg", skel)

	def getDistance(x1,y1,x2,y2):
		return float((x1-x2)**2 + (y1-y2)**2)**.5

	# sort endpoints into pairs for edge combining
	# vertical segments
	for seg in v_endpoints:
		# print(seg)
		end = seg[1]
		print(end)
		# see if there is a segment in a 3x3 area around current segment
		# vertical segments end
		for x in range(-1,1+1,1):
			for y in range(0,2+1,1):
				curr_x = end[0]
				curr_y = end[1]
				new_x = curr_x+x
				new_y = curr_y+y
				if skel[new_y][new_x] == 255 and new_x < w and new_y < h:
					dist = getDistance(curr_x,curr_y,curr_x+x,curr_y+y)
					print("distance",dist)
					if dist <= 3:
						min_x = curr_x
						max_x = new_x
						if new_x < curr_x:
							min_x = new_x
							max_x = curr_x
						min_y = curr_y
						max_y = new_y
						if new_y < curr_y:
							min_y = new_y
							max_y = curr_y

						for j in range(min_x,max_x):
							skel[curr_y][j] = 255
						for j in range(min_y,max_y):
							skel[j][new_x] = 255

						# skel[curr_y][min_x:max_x] = 255
						# skel[min_y:max_y][curr_x] = 255

						print("x:",new_x-curr_x,"y:",new_y-curr_y)

		# do the same thing with tops
		start = seg[0]
		print(start)
		# see if there is a segment in a 3x3 area around current segment
		# vertical segments start
		for x in range(-1,1+1,1):
			for y in range(-2,0+1,1):
				curr_x = start[0]
				curr_y = start[1]
				new_x = curr_x+x
				new_y = curr_y+y
				if skel[new_y][new_x] == 255 and new_x < w and new_y < h:
					dist = getDistance(curr_x,curr_y,curr_x+x,curr_y+y)
					print("distance",dist)
					if dist <= 3:
						min_x = curr_x
						max_x = new_x
						if new_x < curr_x:
							min_x = new_x
							max_x = curr_x
						min_y = curr_y
						max_y = new_y
						if new_y < curr_y:
							min_y = new_y
							max_y = curr_y

						for j in range(min_x,max_x):
							skel[curr_y][j] = 255
						for j in range(min_y,max_y):
							skel[j][new_x] = 255

						# skel[curr_y][min_x:max_x] = 255
						# skel[min_y:max_y][curr_x] = 255

						print("x:",new_x-curr_x,"y:",new_y-curr_y)


		cv2.imwrite("skel combine.jpg", skel)

	# get contours
	ratio = 3
	img_scaled = cv2.resize(skel,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
	cv2.imshow("scaled", img_scaled)
	img_scaled = np.array(img_scaled, dtype=np.uint8)
	cv2.imshow("title wt", img_scaled)
	cpy = img_scaled.copy()
	# img2, cnts, hier = cv2.findContours(img_scaled,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	# cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
	# cv2.drawContours(img_scaled, cnts, -1, (0,255,0), 3)
	# cv2.imshow("cont", img_scaled)

	coords = dipdigits.find_digits(cpy)
	# coords are in x, y, w, h
	print(coords)
	# digits = img_scaled[coords[0][0]:coords[0][0]+coords[0][2], coords[0][1]:coords[0][1]+coords[0][3]]
	# cv2.imshow("digit", digits)
	# dipdigits.identify_digits(skel,coords)
	for i,c in enumerate(coords):
		# extract the digit from the screen picture
		x = c[0]
		y = c[1]
		w = c[2]
		h = c[3]
		roi = img_scaled[y:y + h, x:x + w]
		title = "cropped"+str(i)
		cv2.imshow(title, roi)
		cv2.imwrite("digit"+str(i)+".jpg", roi)

	
cv2.waitKey(0)
cv2.destroyAllWindows()
