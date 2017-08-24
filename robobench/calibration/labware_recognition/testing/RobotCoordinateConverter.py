# TOOD: put everything in row major (since opencv seems to prefer row major)

import cv2
import imutils
import numpy as np
import glob
from opentrons import robot
from inspect import getsourcefile
from os.path import abspath, join, dirname

class RobotCoordinateConverter:
	def __init__(self, camera_calibration_file=None):
		if camera_calibration_file == None:
			absolute_dir_path = abspath(dirname(getsourcefile(lambda:0)))
			camera_calibration_file = join(absolute_dir_path, 'calibration_values.npz') 
		with np.load(camera_calibration_file) as calibration_values:
			self.cam_mtx, self.dist = [calibration_values[i] for i in ('mtx', 'dist')]
			self.rvec = None
			self.tvec = None
			self.obj_to_robot_mtx = None
			self.robot_to_obj_mtx = None

	def draw(self, img, corners, imgpts):
		corner = tuple(corners[0].ravel())
		img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
		img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
		img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
		return img

	def getRobotPoints(self):
		return ((40, 400), (202, 400), (40,292.15))

	def calibrateRobotTransformation(self, robot_points):
		'''
		TODO:
		calibrate z for robot to object
		handle inconsistent points, generalize if needed
		Input: object points (0,0), (6,0), (0,4) in robot_points (3 x 2)
		Output: (robot to object, object to robot) homogeneous transformation matrices
		'''
		t0 = robot_points[0][0]
		t1 = robot_points[0][1]
		r00 = (robot_points[1][0] - t0) / 6
		r01 = (robot_points[1][1]  - t1) / 6
		r10 = (robot_points[2][0] - t0) / 4
		r11 = (robot_points[2][1] - t1) / 4
		obj_to_robot_rot_mtx = np.array([[r00, r01], [r10, r11]])
		robot_to_obj_rot_mtx = np.linalg.inv(obj_to_robot_rot_mtx)
		# print(t0)
		# print(t1)
		tvec_obj_to_robot = np.array([[t0], [t1]])
		tvec_robot_to_obj = np.array([[-t0 * robot_to_obj_rot_mtx[0][0] - t1 * robot_to_obj_rot_mtx[0][1]],
									[-t0 * robot_to_obj_rot_mtx[1][0] - t1 * robot_to_obj_rot_mtx[1][1]]])
		obj_to_robot_mtx = np.concatenate((np.concatenate((obj_to_robot_rot_mtx, tvec_obj_to_robot), axis=1), [[0, 0, 1]]), axis=0)    
		robot_to_obj_mtx = np.concatenate((np.concatenate((robot_to_obj_rot_mtx, tvec_robot_to_obj), axis=1), [[0, 0, 1]]), axis=0)
		return (robot_to_obj_mtx, obj_to_robot_mtx)

	def calibrate(self, img):
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
		objp = np.zeros((7*5, 1, 3), np.float32)
		objp[:,:,:2] = np.mgrid[0:7,  0:5].T.reshape(-1,1,2)
		axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)

		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		#corners are 1x2 points
		ret, corners = cv2.findChessboardCorners(gray, (7,5),None)

		if ret:
			# 1x2 points
			corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
			# don't need inliers?
			_, self.rvec, self.tvec, inliers = cv2.solvePnPRansac(objp, corners2, self.cam_mtx, self.dist)
			# print("rvec: {}".format(self.rvec))
			imgpts, jac = cv2.projectPoints(axis, self.rvec, self.tvec, self.cam_mtx, self.dist)
			img = self.draw(img,corners2,imgpts)
			cv2.drawChessboardCorners(img, (7,5), corners2, ret)
			cv2.imshow('img',img)
			k = cv2.waitKey(0) & 0xff
			cv2.destroyWindow('img')
		else:
			return False

		robot_points = self.getRobotPoints()
		self.robot_to_obj_mtx, self.obj_to_robot_mtx = self.calibrateRobotTransformation(robot_points)
		return True

	def pixelToRobot(self, img_point, z):
		'''
		TODO: make sure z is handled correctly
		Returns world coordinate with given z value above deck (in robot coordinates) of inputted pixel coordinate.
		Input: img_point tuple (u,v) , Z value of world point
		Returns 1x3 world point [[X, Y, Z]]
		'''
		# if img_point.shape != (1, 2):
		# 	raise ValueError('Expects 1x2 numpy rray as img_point, received {}'.format(img_point))

		if len(img_point) != 2:
			raise ValueError('Expects tuple (u,v) of length 2')

		u, v = img_point

		# 3x3 rotation matrix
		rtmtx, _ = cv2.Rodrigues(self.rvec)
		# 3 x 4 rotation transformation matrix
		rt_tr_mtx = np.concatenate((rtmtx, self.tvec), axis=1)
		# complete projection matrix
		transform_mtx = np.dot(self.cam_mtx, rt_tr_mtx)

		# To solve for X,Y given Z, solves
		# desired_vec = desired_mat x [[X,Y]]
		desired_vec = np.array([[transform_mtx[0][2] * z + transform_mtx[0][3] - u * transform_mtx[2][2] * z - u * transform_mtx[2][3]],
								[transform_mtx[1][2] * z + transform_mtx[1][3] - v * transform_mtx[2][2] * z - v * transform_mtx[2][3]]])

		desired_mat = np.array([[u * transform_mtx[2][0] - transform_mtx[0][0], u * transform_mtx[2][1] - transform_mtx[0][1]],
								[v * transform_mtx[2][0] - transform_mtx[1][0], v * transform_mtx[2][1] - transform_mtx[1][1]]])
		inv_dmat = np.linalg.inv(desired_mat)
		print("dvec: {}".format(desired_vec))
		print("dmat: {}".format(desired_mat))
		print("inv_dmat: {}".format(inv_dmat))
		pred = np.dot(inv_dmat, desired_vec)
		print(pred)
		pred_homogeneous = cv2.convertPointsToHomogeneous(pred.transpose())[0].transpose()
		print(self.obj_to_robot_mtx)
		pred_robot = np.dot(self.obj_to_robot_mtx, pred_homogeneous)
		print("pred_robot: {}".format(pred_robot))
		pred_robot[2] = z
		print("Prediction: {}".format(pred_robot))
		prediction_tuple = (pred_robot[0][0], pred_robot[1][0], pred_robot[2][0])
		return pred_robot

	def robotToPixel(self, robot_coord):
		'''
		NEED TO CALIBRATE Z WITH ROBOT POINTS
		Converts from robot coordinate to image coordinate
		Input: robot coordinate (x, y, z)
		Output: 1x2 pixel coordinate (x, y)
		'''
		# converts to object coords from robot coordinates (units are checkerboard squares)
		print(self.robot_to_obj_mtx)
		robot_xy = np.array([[robot_coord[0], robot_coord[1], 1]])
		obj_xy = np.dot(self.robot_to_obj_mtx, robot_xy.transpose())
		print(obj_xy)
		# TODO: change to calibrated transformation
		obj_z = (robot_coord[2] + 82) / -27

		obj_point = np.array([[obj_xy[0][0], obj_xy[1][0], obj_z]]).transpose()
		print(obj_point)

		img_pts, _ = cv2.projectPoints(np.array([obj_point]), self.rvec, self.tvec, self.cam_mtx, self.dist)
		print(img_pts)
		pixel = (img_pts[0][0][0], img_pts[0][0][1])
		return pixel

if __name__ == "__main__":
	converter = RobotCoordinateConverter()
	img = cv2.imread('../calibration/checkerboard_images/img21.jpg')
	converter.calibrate(img)
	print(converter.robot_to_obj_mtx)
	print(converter.obj_to_robot_mtx)
	print(converter.pixelToRobot((388, 146), 0))
	print(converter.pixelToRobot(converter.robotToPixel((40, 400, -82)), 0))