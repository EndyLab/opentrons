import cv2
import imutils
import RobotVision
import math
import matplotlib.pyplot as plt
import sys

ground_truth = [
				# ("images/testset1/tiptest_w1000_3.jpg", (71, 333, -31)),
				# ("images/testset1/tiptest_w1000_4.jpg", (67, 75, -31)),
				# ("images/testset1/tiptest_w1000_5.jpg", (65, 183, -31)),
				# ("images/testset1/tiptest_w1000_6.jpg", (225, 311, -31)),
				# ("images/testset1/tiptest_w1000_7.jpg", (230, 210, -31)),
				# ("images/testset1/tiptest_w1000_8.jpg", (201, 90, -31)),
				# ("images/testset1/tiptest_w1000_9.jpg", (368, 320, -31)),
				# ("images/testset1/tiptest_w1000_10.jpg", (365, 210, -31)),
				# ("images/testset1/tiptest_w1000_11.jpg", (360, 90, -31)), 

				("images/testset1/welltest_w1000_0.jpg", (62, 319, -42)),
				("images/testset1/welltest_w1000_1.jpg", (74, 228, -42)), 
				("images/testset1/welltest_w1000_2.jpg", (79, 108, -42)), 
				("images/testset1/welltest_w1000_3.jpg", (200, 350, -42)), 
				("images/testset1/welltest_w1000_4.jpg", (220, 231, -42)), 
				("images/testset1/welltest_w1000_5.jpg", (215, 75, -42)), 
				("images/testset1/welltest_w1000_6.jpg", (360, 340, -42)), 
				("images/testset1/welltest_w1000_7.jpg", (350, 230, -42)), 
				("images/testset1/welltest_w1000_8.jpg", (338, 60, -42)), 
				]

vision = RobotVision.RobotVision()
x = []
y = []
colors = []
area = []
for example in ground_truth:
	file, true_coords = example
	print(file)
	frame = cv2.imread(file)
	frame = imutils.resize(frame, width=1000)
	frame = vision.converter.undistort(frame)
	name_to_slots_coords_map = vision.evaluate_deck(frame)
	try:
		if 'welltest' in file:
			pred_coords = name_to_slots_coords_map['WellPlate'][0][1]
		elif 'tiptest' in file:
			pred_coords = name_to_slots_coords_map['TipRack'][0][1]
		else:
			print("Unrecognized file")
			continue
	except KeyError:
		print("Failed to detect plate")
		continue	
	print("True coords: {}".format(true_coords))
	print("Pred coords: {}".format(pred_coords))
	offset = (true_coords[0] - pred_coords[0], true_coords[1] - pred_coords[1], true_coords[2] - pred_coords[2])
	x.append(offset[0])
	y.append(offset[1])
	offset_xy = (true_coords[0] - pred_coords[0], true_coords[1] - pred_coords[1])
	distance = math.sqrt(offset[0] ** 2 + offset[1] ** 2 + offset[2] ** 2)
	distance_xy = math.sqrt(offset_xy[0] ** 2 + offset_xy[1] ** 2)
	if distance_xy < 2.5:
		colors.append('green')
	else:
		colors.append('red')
	area.append(35)
	print("Offset: {}".format(offset))
	#print("Offset xy: {}".format(offset_xy))
	print("Distance: {}".format(distance))
	#print("Distance xy: {}".format(distance_xy))

fig, ax = plt.subplots()
maxval = max(x)
maxval2 = max(y)
maxval = max(maxval, maxval2)
maxval = max(maxval, 4)
plt.ylim(-maxval, maxval)
plt.xlim(-maxval, maxval)
circle1 = plt.Circle((0, 0), 2.5, color='k', alpha=.2)
ax.add_artist(circle1)
plt.scatter(x, y, s=area, c=colors, alpha=.5)
ax.set_aspect('equal')

plt.show()
#plt.savefig('/Users/michaelbereket/Desktop/PosterFigures/TiprackPlot.png', dpi=300)
