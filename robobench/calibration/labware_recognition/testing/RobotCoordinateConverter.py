# TODO: put everything in either row major or column major
# TODO: figure out where slight error in conversions is coming from (float precision?)
# TODO: make methods/attributes private
# TODO: add error checking
# TODO: create test harness
# TODO: checkerboard printout issue - last two squares in x direction slightly larger



import cv2
import imutils
import numpy as np
import glob
from opentrons import robot
from inspect import getsourcefile
from os.path import abspath, join, dirname
import math

class RobotCoordinateConverter:
    '''
    Class to convert pixels to robot coordinates
    '''
    def __init__(self, camera_calibration_file=None):
        
        if camera_calibration_file is None:
            absolute_dir_path = abspath(dirname(getsourcefile(lambda:0)))
            camera_calibration_file = join(absolute_dir_path, 'calibration_values.npz') 
        with np.load(camera_calibration_file) as calibration_values:
            self.cam_mtx, self.dist = [calibration_values[i] for i in ('mtx', 'dist')]
            self.rvec = None
            self.tvec = None
            self.obj_to_robot_mtx = None
            self.robot_to_obj_mtx = None
            self.checkerboard_z = None

    def draw(self, img, corners, imgpts, debug=False):
        corner = tuple(corners[0].ravel())
        if debug:
            print("corner for draw: {}".format(corner))
            #print("imgpts[0]: {}".format(imgpts[0]))
        img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
        img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
        img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
        return img

    def getRobotPoints(self):
        # return ((40, 400), (202, 400), (40,292), -82)
        # return ((46, 390), (204, 390), (47.5, 285), -46)
        # checkerboard image 3
        # return ((40, 400), (199, 400), (40, 296), -43)
        # checkerboard image 4
       return ((60, 365), (218, 365), (60, 261), -41)
       # checkerboard image 5
       #return ((70, 370), (228, 370), (70, 292), -41.5)
       #return ((59, 366), (217, 367), (59, 262), -41)
       # checkerboard image 6
       #return ((32, 390), (190, 390), (32, 285), -41.5)
       #return ((34, 392), (192, 392), (34, 287), -41.5)
       # checkerboard image 7
       #return ((125, 215), (284, 215), (125, 109), -41)

    def calibrateRobotTransformation(self, robot_points, debug=False):
        '''
        Calibrates transformations between robot and object (checkerboard) coordinates

        Args:
            robot_points(tuple): xy of robot coordinates corresponding to ((0,0), (6,0), (0,4), z value of deck) as tuple

        Returns:
            (robot_to_obj_mtx, obj_to_robot_mtx): 3x3 matrices to convert between robot (x,y) and object (x,y)
            also sets self.checkerboard_z and self.object_to_robot_scale, which allows conversion between z values

        TODO:
        handle inconsistent points, generalize if needed
        '''
        t0 = robot_points[0][0]
        t1 = robot_points[0][1]
        r00 = (robot_points[1][0] - t0) / 6
        r01 = (robot_points[1][1]  - t1) / 6
        r10 = (robot_points[2][0] - t0) / 4
        r11 = (robot_points[2][1] - t1) / 4
        # 2x2 matrix to line up object and robot axes
        obj_to_robot_rot_mtx = np.array([[r00, r01], [r10, r11]])
        robot_to_obj_rot_mtx = np.linalg.inv(obj_to_robot_rot_mtx)
        # print(t0)
        # print(t1)
        # translation for origin between object to robot
        tvec_obj_to_robot = np.array([[t0], [t1]])
        # translation for origin between robot and object coords
        # accounts for rotation between coords
        tvec_robot_to_obj = np.array([[-t0 * robot_to_obj_rot_mtx[0][0] - t1 * robot_to_obj_rot_mtx[0][1]],
                                    [-t0 * robot_to_obj_rot_mtx[1][0] - t1 * robot_to_obj_rot_mtx[1][1]]])
        obj_to_robot_mtx = np.concatenate((np.concatenate((obj_to_robot_rot_mtx, tvec_obj_to_robot), axis=1), [[0, 0, 1]]), axis=0)    
        robot_to_obj_mtx = np.concatenate((np.concatenate((robot_to_obj_rot_mtx, tvec_robot_to_obj), axis=1), [[0, 0, 1]]), axis=0)
        # checkerboard should be flat so each point should have same z value
        self.checkerboard_z = robot_points[3]
        self.object_to_robot_scale = math.sqrt(obj_to_robot_mtx[0][0] ** 2 + obj_to_robot_mtx[1][0] ** 2)

        return (robot_to_obj_mtx, obj_to_robot_mtx)

    def calibrate(self, img, debug=False):
        '''
        Calibrates coordinate converter

        Args:
            img(cv2::Mat): image with checkerboard lying flat on the deck

        Returns:
            boolean: whether successful or not
        '''

        if debug:
            print("In calibrate")
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objp = np.zeros((7*5, 1, 3), np.float32)
        objp[:,:,:2] = np.mgrid[0:7,  0:5].T.reshape(-1,1,2)
        axis = np.float32([[15,0,0], [0,15,0], [0,0,-15]]).reshape(-1,3)

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #corners are 1x2 points
        ret, corners = cv2.findChessboardCorners(gray, (7,5),None)

        if ret:
            # 1x2 points
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            _, self.rvec, self.tvec, _ = cv2.solvePnPRansac(objp, corners2, self.cam_mtx, self.dist)
            # print("rvec: {}".format(self.rvec))
            # 1x2 points
            imgpts, jac = cv2.projectPoints(axis, self.rvec, self.tvec, self.cam_mtx, self.dist)
            # print("imgpts: {}".format(imgpts))
            img = self.draw(img,corners2,imgpts, debug)
            cv2.drawChessboardCorners(img, (7,5), corners2, ret)
            if debug:
                cv2.imshow('img',img)
                k = cv2.waitKey(0) & 0xff
                cv2.destroyWindow('img')
        else:
            return False

        robot_points = self.getRobotPoints()
        self.robot_to_obj_mtx, self.obj_to_robot_mtx = self.calibrateRobotTransformation(robot_points)
        return True

    def pixelToRobot(self, img_point, robot_z, debug=False):
        '''
        TODO: make sure z is handled correctly
        Returns robot coordinates of passed in pixel given z value in robot coordinates

        Args:
            img_point(tuple): pixel as (u,v)
            robot_z(float): z value pixel in robot coordinates

        Returns:
            tuple: robot coordinate (x, y, z) of pixel with given z value
        '''

        if len(img_point) != 2:
            raise ValueError('Expects tuple (u,v) of length 2')

        u, v = img_point 
        # 3x3 rotation matrix
        rtmtx, _ = cv2.Rodrigues(self.rvec)
        # 3 x 4 rotation transformation matrix
        rt_tr_mtx = np.concatenate((rtmtx, self.tvec), axis=1)
        # complete projection matrix
        transform_mtx = np.dot(self.cam_mtx, rt_tr_mtx)

        # obj_z = (robot_z + 82) / -27
        obj_z = (robot_z - self.checkerboard_z) / -abs(self.object_to_robot_scale)
        if debug:
            print("checkerboard_z: {}".format(self.checkerboard_z))
            print("object_to_robot_scale: {}".format(self.object_to_robot_scale))
            print("obj_z: {}".format(obj_z))
            # print("cam_mtx: {}".format(self.cam_mtx))
            # print("rttr matrix: {}".format(rt_tr_mtx))
            # print("transform mtx: {}".format(transform_mtx))

        # To solve for X,Y given Z, solves
        # desired_vec = desired_mat x [[X,Y]]
        # equation accounts for homogeneous coordinates
        desired_vec = np.array([[transform_mtx[0][2] * obj_z + transform_mtx[0][3] - u * transform_mtx[2][2] * obj_z - u * transform_mtx[2][3]],
                           [transform_mtx[1][2] * obj_z + transform_mtx[1][3] - v * transform_mtx[2][2] * obj_z - v * transform_mtx[2][3]]])

        desired_mat = np.array([[u * transform_mtx[2][0] - transform_mtx[0][0], u * transform_mtx[2][1] - transform_mtx[0][1]],
                                [v * transform_mtx[2][0] - transform_mtx[1][0], v * transform_mtx[2][1] - transform_mtx[1][1]]])

        # print("dvec: {}".format(desired_vec))
        # print("dmat: {}".format(desired_mat))
        inv_dmat = np.linalg.inv(desired_mat)
        # print("dvec: {}".format(desired_vec))
        # print("dmat: {}".format(desired_mat))
        # print("inv_dmat: {}".format(inv_dmat))
        pred = np.dot(inv_dmat, desired_vec)
        # print("Object prediction: {}".format(pred))
        pred_homogeneous = cv2.convertPointsToHomogeneous(pred.transpose())[0].transpose()
        # print(self.obj_to_robot_mtx)
        pred_robot = np.dot(self.obj_to_robot_mtx, pred_homogeneous)
        # print("pred_robot: {}".format(pred_robot))
        pred_robot[2] = robot_z
        if debug:
            print("Prediction: {}".format(pred_robot))
        prediction_tuple = (pred_robot[0][0], pred_robot[1][0], pred_robot[2][0])
        return prediction_tuple

    def robotToPixel(self, robot_coord, round_vals=True, debug=False):
        '''
        Converts from robot coordinate to image coordinate

        Args:
            robot_coord(tuple): robot coordinate (x, y, z)
            round_vals(boolean, optional): whether to round values to ints, default True
        
        Returns: 
            tuple: pixel coordinate (u, v)
        '''
        # converts to object coords from robot coordinates (units are checkerboard squares)
        robot_xy = np.array([[robot_coord[0], robot_coord[1], 1]])
        obj_xy = np.dot(self.robot_to_obj_mtx, robot_xy.transpose())
        print(obj_xy)
        #print(obj_xy)
        # -z for checkerboard comes out to camera, squares so scaling should be same x axis
        # obj_z = (robot_coord[2] + 82) / -27
        # print("obj_z 1: {}".format(obj_z))
        obj_z = (robot_coord[2] - self.checkerboard_z) / -abs(self.object_to_robot_scale)
        #print(self.checkerboard_z)
        #print(self.object_to_robot_scale)
        #print("obj_z 2: {}".format(obj_z))

        obj_point = np.array([[obj_xy[0][0], obj_xy[1][0], obj_z]]).transpose()
        #print("Object point: {}".format(obj_point))

        img_pts, _ = cv2.projectPoints(np.array([obj_point]), self.rvec, self.tvec, self.cam_mtx, self.dist)
        #print(img_pts)
        pixel = (img_pts[0][0][0], img_pts[0][0][1])
        if round_vals:
            pixel = (int(round(pixel[0])), int(round(pixel[1])))
        return pixel

if __name__ == "__main__":
    converter = RobotCoordinateConverter()
    # img = cv2.imread('../calibration/checkerboard_images/img21.jpg')
    img = cv2.imread('VisionTestingImages/checkerboardimg4.jpg')
    converter.calibrate(img, debug=True)
    #cam = cv2.VideoCapture(0)
    # while True:
    #     _, img = cam.read()
    #     img = imutils.resize(img, width=1000)
    for i in range(-3, 15):
        for j in range(-3, 15):
            for k in range(2):
                # Should be able to have one as the argument for the other
                space = converter.object_to_robot_scale
                p1 = converter.robotToPixel((60 + space * i, 365 - space * j, converter.checkerboard_z + k * space))
                #p2 = converter.robotToPixel((60 + space * i, 365 - space * j, 8))
                p3 = converter.robotToPixel((60 + space * (i + 1), 365 - space * j, converter.checkerboard_z + k * space))
                p4 = converter.robotToPixel((60 + space * i, 365 - space * (j + 1), converter.checkerboard_z + k * space))
                # a1
                # p5 = converter.robotToPixel((60 + space * i + 11, 365 - space * j + 14, converter.checkerboard_z + space))
                p6 = converter.robotToPixel((60 + space * i, 365 - space * j, converter.checkerboard_z + space * (k+1)))
                p7 = converter.robotToPixel((60 + space * (i + 1), 365 - space * j, converter.checkerboard_z + space * (k+1)))
                p8 = converter.robotToPixel((60 + space * i, 365 - space * (j + 1), converter.checkerboard_z + space * (k+1)))

                print("p1: {}".format(p1))
                cv2.line(img, p1, p3, (0, 255, 0), 1)
                cv2.line(img, p1, p4, (0, 255, 0), 1)
                cv2.line(img, p1, p6, (0, 255, 0), 1)
                cv2.line(img, p6, p7, (0, 255, 0), 1)
                cv2.line(img, p6, p8, (0, 255, 0), 1)
            # cv2.line
            # cv2.circle(img, p5, 3, (255, 100, 100), -1)
            #cv2.line(img, p2, p4, ((5 * i + 100) % 255, 0, (5 * j + 150) % 255), 3)
    cv2.imshow("img", img)
    cv2.imwrite("/Users/michaelbereket/Desktop/PosterFigures/grid.jpg", img)
        # key = cv2.waitKey(1) & 0xff
        # if key == ord('q'):
        #     break

    print(converter.robot_to_obj_mtx)
    print(converter.obj_to_robot_mtx)
    cv2.waitKey(0)
    print("Test inverse")
    #print(converter.object_to_robot_scale)
    print(converter.pixelToRobot(converter.robotToPixel((40, 400, 0), False), 0))
    print("Test conversion: {}".format(converter.pixelToRobot((500, 495), 0)))

    #print(converter.pixelToRobot((308, 149.2), 0))
    #print(converter.pixelToRobot(converter.robotToPixel((40, 400, 0)), 82))