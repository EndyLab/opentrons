import cv2
import sys
import numpy as np
import imutils

#ADD ERROR CHECKING

def findA1(src):
	'''
	Takes as input a cropped 96 well plate image (opencv Mat)
	Currently optimized for clear plate on dark background
	Returns location of center of A1 well and radius as (x, y, r)
	Assumes A1 is bottom left
	'''
	well_list = findWells(src)
	return well_list[11]


def findWells(src):
	'''
	Takes as input a grayscale, cropped 96 well plate image (opencv Mat)
	Currently optimized for clear plate on dark background
	Returns a sorted list of wells (x,y)
	'''
	img = src.copy()
	boxes = findWellBoxes(img)
	imw = img.shape[0]
	imh = img.shape[1]
	print("img w/h: {}/{}".format(imw, imh))
	well_drawing = np.zeros((imw, imh, 3), np.uint8)
	# all_drawing = np.zeros((imw, imh, 3), np.uint8)
	for box in boxes:
		x,y,w,h = box
		# cv2.rectangle(all_drawing, (x,y), (x+w,y+h), (0,255,0),2)
		if validWellBox(box, img):
			#print((x, y, w, h))
			cv2.rectangle(well_drawing, (x,y), (x+w,y+h), (0,255,0),2)
	cv2.namedWindow("contours")
	cv2.imshow("contours", well_drawing)
	# cv2.namedWindow("all window")
	# cv2.imshow("all window", all_drawing)
	well_list = determineWellPositions(boxes, img)
	well_list.sort()
	#pred_drawing = np.zeros((imw, imh, 3), np.uint8)
	for well in well_list:
		x, y = well
		# print(x)
		# print(y)
		cv2.rectangle(img, (x-3, y-3), (x+3, y+3), (255, 0, 0), 2)	
	x1, y1 = well_list[11]
	cv2.rectangle(img, (x1-3, y1-3), (x1+3, y1+3), (255, 255, 0), 3)	
	cv2.namedWindow("predicted wells")
	cv2.imshow("predicted wells", img)
	print(well_list)
	return well_list

	#JUST FOR TESTING
	#cv2.imwrite(sys.argv[1][:-4] + sys.argv[2] + ".jpg", img)

def determineWellPositions(boxes, img):
	'''
	Takes as input a list of bounding rects that should bound most wells and not bound many other objects
	Returns a dictionary of {slot:(x,y)} that gives an approx of the centers of the well
	'''
	potential_col_x = {}
	potential_row_y = {}
	# find x and y locations that correspond to the most boxes
	for box in boxes:
		x, y, w, h = box
		addVote(x, int(w / 2), potential_col_x)
		addVote(y, int(h / 2), potential_row_y)
	print(potential_col_x)
	print(potential_row_y)
	# sort x and y candidates by votes
	x_candidates = [(k, potential_col_x[k]) for k in sorted(potential_col_x, key=potential_col_x.get, reverse=True)]
	y_candidates = [(k, potential_row_y[k]) for k in sorted(potential_row_y, key=potential_row_y.get, reverse=True)]
	# select top 8 or 12 positions
	x_candidates = x_candidates[:8]
	y_candidates = y_candidates[:12]
	print("x_candidates: {}".format(x_candidates))
	print("y_candidates: {}".format(y_candidates))
	# relate c to average well size?
	x_center = img.shape[1] / 2
	x_candidates = validate_well_candidates(x_candidates, 8, 5, x_center, True)
	y_center = img.shape[0] / 2
	y_candidates = validate_well_candidates(y_candidates, 12, 5, y_center, False)
	well_list = []
	for x in x_candidates:
		for y in y_candidates:
			well_list.append((x[0],y[0]))
	return well_list

def validate_well_candidates(candidates, expected_num, c, center, x_axis):
	'''
	Post processing on well approximations
	Returns a refined guess
	'''
	# Approximate average delta between positions
	delta_candidates = {}
	candidates.sort(key=lambda t: t[0])
	print("Candidates: {}".format(candidates))
	for i in range(1, len(candidates)):
		delta = candidates[i][0] - candidates[i-1][0]
		weight = (candidates[i][1] + candidates[i - 1][1]) / 2
		addVote(delta - c, 2 * c, delta_candidates, weight) 
	print("Delta candidates: {}".format(delta_candidates))
	expected_delta = max(delta_candidates, key=delta_candidates.get)
	print("Expected delta: {}".format(expected_delta))
	# change to while so adapts with insertions
	print(expected_delta)
	i = 1
	while i < len(candidates):
		print(i)
		#increment = True
		delta = candidates[i][0] - candidates[i-1][0]
		mult = abs(round(delta / expected_delta))
		print("Delta: {} Mult: {}".format(delta, mult))
		if mult > 1:
			if candidates[i][1] > candidates[i-1][1]:
				for j in range(1, mult):
					new_pos = candidates[i][0] - expected_delta * j
					new_weight = candidates[i][1] - 1 # need to change
					candidates.insert(i, (new_pos, new_weight))
					print("inserted at {}".format(i))
					i = i + 1
					print(candidates)
					cv2.waitKey(0)
			else:
				for j in range(1, mult):
					new_pos = candidates[i-1][0] + expected_delta * j
					new_weight = candidates[i-1][1] - 1 # need to change
					candidates.insert(i, (new_pos, new_weight))
					print("inserted at {}".format(i-1))
		elif mult == 0:
			if candidates[i][1] > candidates[i-1][1]:
				del candidates[i-1]
			else:
				del candidates[i]
			i = i - 1

		i = i + 1
		# cv2.waitKey(0)

		print(candidates)
	while len(candidates) < expected_num:
		# make it centered
		avg = 0
		for t in candidates:
			avg = avg + t[0]
		avg = avg / len(candidates)
		print("avg: {}".format(avg))
		print("center: {}".format(center))
		if center > avg and x_axis or center < avg and not x_axis:
			# add to end
			new_pos = candidates[len(candidates) - 1][0] + expected_delta
			new_weight = candidates[len(candidates) - 1][1] - 1 # need to look at again
			candidates.append((new_pos, new_weight))
		else:
			new_pos = candidates[0][0] - expected_delta
			new_weight = candidates[0][1] - 1 # need to look at again
			candidates.insert(0, (new_pos, new_weight))
		print(candidates)

	candidates.sort(key = lambda t: t[1], reverse=True)
	return candidates[:expected_num]
		# if abs(delta - expected_delta) > 2 * c:
	# 		# need to allow for gaps greater than 1 row/column
	# 		if candidates[i][1] > candidates[i-1][1]:
	# 			new_pos = candidates[i][0] - expected_delta
	# 			increment = False
	# 		else:
	# 			new_pos = candidates[i-1][0] + expected_delta
	# 		weight = (candidates[i][1] + candidates[i - 1][1]) / 2
	# 		candidates.insert(i, (new_pos, weight))
	# 		print(candidates)
	# 	if increment:
	# 		i = i + 1

	#candidates.sort(key=lambda t: scoreByNeighborPositions(t, candidates, expected_delta, expected_num, c), reverse=True)
	# scored_candidates = [(t[0], scoreByNeighborPositions(t, candidates, expected_delta, expected_num, c)) for t in candidates]
	# scored_candidates.sort(key=lambda t: t[1], reverse=True)
	# print("Candidates: {}".format(candidates))
	# print("Scored: {}".format(scored_candidates))
	# candidates = candidates[:expected_num]
	# return candidates

def scoreByNeighborPositions(curr, candidates, expected_delta, expected_num, c):
	score = 0
	print('Check parameters: {}\n{}\n{}\n{}\n{}'.format(curr, candidates, expected_delta, expected_num, c))
	for t in candidates:
		print('t: {}'.format(t))
		delta = t[0] - curr[0]
		mult = abs(round(delta / expected_delta))
		if mult <= expected_num and delta - mult * expected_delta < 2 * c:
			score = score + t[1]
	print('Curr: {} Score: {}'.format(curr, score))
	return score

def addVote(minpos, r, potential_dict, weight=1):
	center = int(minpos + r)
	#print(center)
	#print('r: {}'.format(r))
	#print(potential_dict)
	print('minpos: {} r: {} range: {}'.format(minpos, r, range(minpos, minpos + r + 1)))
	# check if any location buckets exist within given range, if so add vote to that bucket and return
	for pos in range(minpos, minpos + r + 1):
		if pos in potential_dict.keys():
			# print(pos)
			potential_dict[pos] = potential_dict[pos] + weight
			#print(pos)
			return
	center = int(minpos + r/2)
	#print(center)
	# no existing location bucket exists, 
	potential_dict[center] = weight

def validWellBox(box, img):
	x,y,w,h = box
	imw = img.shape[0]
	imh = img.shape[1]
	return (w / h > .5 and w / h < 2 and imw / w < 35 and imw / w > 15 and imh / h < 50)
	# return (w / h > .5 and w / h < 2 and imw / w < 30 and imw / w > 15 and imh / h < 40)
	# return True



def findWellBoxes(img):
	'''
	Takes as input a grayscale, cropped 96 well plate image (opencv Mat)
	Currently optimized for clear plate on dark background
	Processes image and returns list of bounding boxes ideally bound a majority
	of the wells and are majority bounding wells
	'''
	clahe = cv2.createCLAHE()
	img = clahe.apply(img)
	img = cv2.blur(img, (10,10))
	cv2.namedWindow("source window")
	cv2.imshow("source window", img)
	ret, thresh = cv2.threshold(img, .75 * np.average(img), 255, cv2.THRESH_BINARY_INV)
	cv2.imshow("thresh", thresh)
	im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	boxes = [cv2.boundingRect(cnt) for cnt in contours]
	boxes = [box for box in boxes if validWellBox(box, img)]
	return boxes

if __name__ == "__main__":
	src = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
	src = imutils.resize(src, width=300)
	print(findA1(src))
	cv2.waitKey(0)