import cv2
import imutils
import RobotVision3
import math

ground_truth = {"VisionTestingImages/wellplatedeck1.jpg" : (0, 0, 0)}

vision = RobotVision3.RobotVision()
for file, true_coords in ground_truth.items():
	print(file)
	frame = cv2.imread(file)
	frame = imutils.resize(frame, width=1000)
	name_to_slots_coords_map = vision.evaluate_deck(frame)
	try:
		pred_coords = name_to_slots_coords_map['WellPlate'][0][1]
	except KeyError:
		print("Failed to detect plate")
		continue	
	print("True coords: {}".format(true_coords))
	print("Pred coords: {}".format(pred_coords))
	offset = (true_coords[0] - pred_coords[0], true_coords[1] - pred_coords[1], true_coords[2] - pred_coords[2])
	distance = math.sqrt(offset[0] ** 2 + offset[1] ** 2 + offset[2] ** 2)
	print("Offset: {}".format(offset))
	print("Distance: {}".format(distance))
