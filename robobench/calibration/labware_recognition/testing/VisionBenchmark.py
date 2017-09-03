import cv2
import imutils
import RobotVision3
import math
import matplotlib.pyplot as plt

ground_truth = [
				# ("VisionTestingImages/platetest1.jpg", (43, 296, -41)),
				# ("VisionTestingImages/platetest2.jpg", (39.5, 220.5, -41)),
				# ("VisionTestingImages/platetest3.jpg", (26, 70, -41)),
				# ("VisionTestingImages/platetest4.jpg", (152, 308, -41)),
				# ("VisionTestingImages/platetest5.jpg", (153.5, 223, -41)),
				# ("VisionTestingImages/platetest6.jpg", (134, 92, -41)),
				# ("VisionTestingImages/platetest7.jpg", (227.5, 196, -41)),
				# ("VisionTestingImages/platetest8.jpg", (321.5, 313, -41)),
				# ("VisionTestingImages/platetest9.jpg", (358, 183, -41)),
				# ("VisionTestingImages/platetest10.jpg", (360, 83, -41)), 
				# ("VisionTestingImages/platetest11.jpg", (320, 60, -41)),
				# ("VisionTestingImages/platetest12.jpg", (250, 120, -41)),
				# ("VisionTestingImages/platetest13.jpg", (189, 280, -41)),
				# ("VisionTestingImages/platetest14.jpg", (300, 200, -41)),
				# ("VisionTestingImages/platetest15.jpg", (335, 300, -41)),
				# ("VisionTestingImages/platetest16.jpg", (50, 310, -41)),
				# ("VisionTestingImages/platetest17.jpg", (69.825, 110.75, -41)),
				# ("VisionTestingImages/platetest18.jpg", (90, 130, -41)),
				("VisionTestingImages/tiptest1.jpg", (44, 291.5, -31)),
				("VisionTestingImages/tiptest2.jpg", (36, 207, -31)),
				("VisionTestingImages/tiptest3.jpg", (46.5, 121, -31)),
				("VisionTestingImages/tiptest4.jpg", (214, 328, -31)),
				("VisionTestingImages/tiptest5.jpg", (194, 213, -31)),
				("VisionTestingImages/tiptest6.jpg", (202, 183.5, -31)),
				("VisionTestingImages/tiptest7.jpg", (200.5, 63, -31)),
				("VisionTestingImages/tiptest8.jpg", (346, 299, -31)),
				("VisionTestingImages/tiptest9.jpg", (343.5, 223.5, -31)),
				("VisionTestingImages/tiptest10.jpg", (353.5, 96, -31)),
				("VisionTestingImages/tiptest11.jpg", (89, 84, -31)),
				("VisionTestingImages/tiptest12.jpg", (113, 212, -31)),
				("VisionTestingImages/tiptest13.jpg", (133, 307, -31)),
				("VisionTestingImages/tiptest14.jpg", (213, 91, -31)),
				("VisionTestingImages/tiptest15.jpg", (199, 202, -31)),
				("VisionTestingImages/tiptest16.jpg", (249, 300, -31)),
				("VisionTestingImages/tiptest17.jpg", (315, 262, -31)),
				("VisionTestingImages/tiptest18.jpg", (334, 138, -31))
				]

vision = RobotVision3.RobotVision()
x = []
y = []
colors = []
area = []
for example in ground_truth:
	file, true_coords = example
	print(file)
	frame = cv2.imread(file)
	frame = imutils.resize(frame, width=1000)
	name_to_slots_coords_map = vision.evaluate_deck(frame)
	try:
		if 'platetest' in file:
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
plt.ylim(-4, 4)
plt.xlim(-4, 4)
circle1 = plt.Circle((0, 0), 2.5, color='k', alpha=.2)
ax.add_artist(circle1)
plt.scatter(x, y, s=area, c=colors, alpha=.5)
ax.set_aspect('equal')

plt.show()
#plt.savefig('/Users/michaelbereket/Desktop/PosterFigures/TiprackPlot.png', dpi=300)
