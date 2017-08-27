import cv2
from inspect import getsourcefile
from os.path import abspath, join, dirname

class FineTuner:

	def __init__(self):
		pass

	def get_calibration_coordinates(self, object_type, box, image):
		'''
		Returns robot calibration coordinates for passed in object.

		Args:
			object_type(str): type of object # TODO: error if not in classes
			box (tuple of ints): bounding box of object in image in format (ymin, xmin, ymax, xmax)
			image (cv2::Mat): uncropped image

		Returns:
			tuple (x, y, z) robot calibration coordinates for object
		'''
