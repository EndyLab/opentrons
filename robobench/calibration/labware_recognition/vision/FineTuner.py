import cv2
from inspect import getsourcefile
from os.path import abspath, join, dirname
from RobotCoordinateConverter import RobotCoordinateConverter
import numpy as np
import math

class FineTuner:


    # TODO: remeasure values using robot? Currently assuming robot mm is accurate
    # TODO: measure point values properly
    # tiprack offset x 10, y 14 initially
    # (51, 315) --> (40.5, 301)
    measurements = {# 'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 8, 'welloffset_y' : 7, 'height_green' : 54, 'height_tip' : 64.5, 'tip_offset' : 54.5},
                    #'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 7, 'welloffset_y' : 5.5, 'height_green' : 54, 'height_tip' : 64.5, 'tip_offset' : 54.5},
                    'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 9, 'welloffset_y' : 11, 'height_green' : 54, 'height_tip' : 64.5, 'tip_offset' : 54.5},
                    #'WellPlate' : {'height_well' : 0, 'height_top': 11, 'welloffset_x' : 10.5, 'welloffset_y' : 10, 'length' : 127.33, 'width' : 85},
                    'WellPlate' : {'height_well' : 0, 'height_top': 11, 'welloffset_x' : 10.5, 'welloffset_y' : 14.5, 'length' : 127.33, 'width' : 85},
                    'Trash' : {'height': 50},
                    'Scale' : {'height' : 22},
                    'Trough' : {'height': 20}
                    }

    def __init__(self, converter):
        # Initialize coordinate converter
        # Assign classes to analysis functions
        self.converter = converter

    def get_calibration_coordinates(self, object_type, box, image, debug=False):
        '''
        Returns robot calibration coordinates for passed in object.

        Args:
            object_type(str): type of object # TODO: error if not in classes
            box (tuple of ints): bounding box of object in image in format (ymin, xmin, ymax, xmax)
            image (cv2::Mat): uncropped image

        Returns:
        	tuple (x, y, z) robot calibration coordinates for object
        '''
        if object_type == "TipRack":
            coordinates = self.find_tiprack_a1(box, image, debug)
        elif object_type == "WellPlate":
            coordinates = self.find_wellplate_a1(box, image, debug)
        elif object_type == "Trash" or object_type == "Trough" or object_type == "Scale":
            coordinates = self.find_point_coordinates(object_type, box, image, debug)
        else:
            coordinates = 'Unknown object'
        return coordinates

    def getCorners(self, box_points, crop_top_left):
        ''' Returns top_left, bottom_left, bottom_right points from passed in box_points (from minarearect) and top left point of crop '''
        box_points = np.int0(box_points)
        print(box_points)
        left_to_right = sorted(box_points, key=lambda x: x[0])

        if left_to_right[0][1] > left_to_right[1][1]:
            bottom_left = (left_to_right[0][0] + crop_top_left[0], left_to_right[0][1] + crop_top_left[1])
            top_left = (left_to_right[1][0] + crop_top_left[0], left_to_right[1][1] + crop_top_left[1])
        else:
            bottom_left = (left_to_right[1][0] + crop_top_left[0], left_to_right[1][1] + crop_top_left[1])
            top_left = (left_to_right[0][0] + crop_top_left[0], left_to_right[0][1] + crop_top_left[1])

        if left_to_right[2][1] > left_to_right[3][1]:
            bottom_right = (left_to_right[2][0] + crop_top_left[0], left_to_right[2][1] + crop_top_left[1])
        else:
            bottom_right = (left_to_right[3][0] + crop_top_left[0], left_to_right[3][1] + crop_top_left[1])

        return (top_left, bottom_left, bottom_right)


    def find_tiprack_a1(self, box, image, debug=False):
        height, width, _ = image.shape
        crop_top_left = (int(box[1] * width - 10), int(box[0] * height - 10))
        cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        cropped_height, cropped_width, _ = cropped_image.shape
        frame_to_thresh = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(frame_to_thresh, (58, 67, 0), (78, 255, 255))

        if debug:
            cv2.imshow("thresh", thresh)
            cv2.waitKey(0)
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key=lambda x: cv2.contourArea(x))
        #cv2.drawContours(cropped_image, [max_contour], -1, (0,255,0), 3)
        if debug:
            cv2.imshow("Contours", cropped_image)

        tiprack_vals = self.measurements['tiprack-200ul']
        rect = cv2.minAreaRect(max_contour)
        box = cv2.boxPoints(rect)
        top_left, bottom_left, bottom_right = self.getCorners(box, crop_top_left)
        # box = np.int0(box)
        # print(box)
        # left_to_right = sorted(box, key=lambda x: x[0])
        # print(left_to_right)
        # if left_to_right[0][1] > left_to_right[1][1]:
        #     bottom_left = (left_to_right[0][0] + crop_top_left[0], left_to_right[0][1] + crop_top_left[1])
        #     top_left = (left_to_right[1][0] + crop_top_left[0], left_to_right[1][1] + crop_top_left[1])
        # else:
        #     bottom_left = (left_to_right[1][0] + crop_top_left[0], left_to_right[1][1] + crop_top_left[1])
        #     top_left = (left_to_right[0][0] + crop_top_left[0], left_to_right[0][1] + crop_top_left[1])

        # if left_to_right[2][1] > left_to_right[3][1]:
        #     bottom_right = (left_to_right[2][0] + crop_top_left[0], left_to_right[2][1] + crop_top_left[1])
        # else:
        #     bottom_right = (left_to_right[3][0] + crop_top_left[0], left_to_right[3][1] + crop_top_left[1])

        robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
        robot_bottom_right = self.converter.pixelToRobot(bottom_right, self.converter.checkerboard_z + tiprack_vals['height_green'])
        robot_top_left = self.converter.pixelToRobot(top_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
        bottom_offset = (robot_bottom_right[0] - robot_bottom_left[0], robot_bottom_right[1] - robot_bottom_left[1])
        bottom_dist = math.sqrt(bottom_offset[0] ** 2 + bottom_offset[1] ** 2)
        left_offset = (robot_top_left[0] - robot_bottom_left[0], robot_top_left[1] - robot_bottom_left[1])
        left_dist = math.sqrt(left_offset[0] ** 2 + left_offset[1] ** 2)
        if debug:
            print("robot_bottom_left: {}".format(robot_bottom_left))
            print("robot_bottom_right: {}".format(robot_bottom_right))
            print("robot_top_left: {}".format(robot_top_left))
            print("left_offset: {}".format(left_offset))
            print("bottom offset: {}".format(bottom_offset))
            print("bottom dist: {}".format(bottom_dist))
            print("left_dist: {}".format(left_dist))

        displace_x = left_offset[0]  / left_dist * tiprack_vals['welloffset_y'] + bottom_offset[0] / bottom_dist * tiprack_vals['welloffset_x']
        displace_y = left_offset[1]  / left_dist * tiprack_vals['welloffset_y'] + bottom_offset[1] / bottom_dist * tiprack_vals['welloffset_x']

        robot_a1 = (robot_bottom_left[0] + displace_x, robot_bottom_left[1] + displace_y, -31)
        return robot_a1

    def find_wellplate_a1(self, box, image, debug=False):
        height, width, _ = image.shape
        crop_top_left = (int(box[1] * width - 10), int(box[0] * height - 10))
        cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        cropped_height, cropped_width, _ = cropped_image.shape
        frame_to_thresh = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(frame_to_thresh, (0, 0, 140), (255, 255, 255))
        # night time, need to generalize to work in different conditions
        # thresh = cv2.inRange(frame_to_thresh, (0, 0, 100), (255, 255, 255))
        if debug:
            cv2.imshow("thresh", thresh)
            cv2.waitKey(0)
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key=lambda x: cv2.contourArea(x))
        
        # rect = cv2.minAreaRect(max_contour)
        # box = cv2.boxPoints(rect)
        # top_left, bottom_left, bottom_right = self.getCorners(box, crop_top_left)
        wellplate_vals = self.measurements['WellPlate']
        
        x,y,w,h = cv2.boundingRect(max_contour)
        # bottom left of bounding box relative to uncropped image
        ref_point = (x + crop_top_left[0], y + h + crop_top_left[1])
        # # naive attempt
        # a1_pixel2 = (int(ref_point[0] + 11 / 85 * w), int(ref_point[1] - 14 / 127.33 * h))
        # a1_robot2 = self.converter.pixelToRobot(a1_pixel2, self.converter.checkerboard_z + wellplate_vals['height_well'])
        
        if debug:
            print(rect)
            print("a1 robot naive: {}".format(a1_robot2))

        if crop_top_left[0] >= width / 2 and crop_top_left[1] <= height / 2:
            if True:
                print("Top right")
            # top right, means bottom left of bounding box is actually base level of bottom left of 96 wellplate
            robot_ref_point = self.converter.pixelToRobot(ref_point, self.converter.checkerboard_z)
            robot_a1 = (robot_ref_point[0] + wellplate_vals['welloffset_x'],
                        robot_ref_point[1] + wellplate_vals['welloffset_y'],
                        robot_ref_point[2] + wellplate_vals['height_well'])
        elif crop_top_left[0] <= width / 2 and crop_top_left[1] >= height / 2:
            if True:
                print("Bottom left")
            # bottom left --> bottom left of bounding box is defined by raised edges of wellplate
            robot_ref_point = self.converter.pixelToRobot(ref_point, self.converter.checkerboard_z + wellplate_vals['height_top'])
            robot_a1 = (robot_ref_point[0] + wellplate_vals['welloffset_x'],
                        robot_ref_point[1] + wellplate_vals['welloffset_y'],
                        robot_ref_point[2] - wellplate_vals['height_top'] + wellplate_vals['height_well'])
        elif crop_top_left[0] > width / 2 and crop_top_left[1] > height / 2:
            if True:
                print("Bottom right")
            # bottom right --> bottom left of bounding box is defined by raised bottom and lower left
            robot_ref_point = self.converter.pixelToRobot(ref_point, self.converter.checkerboard_z + wellplate_vals['height_top'])
            robot_ref_point2 = (robot_ref_point[0], robot_ref_point[1], robot_ref_point[2] - wellplate_vals['height_top'])
            ref_point2 = self.converter.robotToPixel(robot_ref_point2)
            bottom_left = (ref_point[0], ref_point2[1])
            robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
            robot_a1 = (robot_bottom_left[0] + wellplate_vals['welloffset_x'],
                        robot_bottom_left[1] + wellplate_vals['welloffset_y'],
                        robot_bottom_left[2] + wellplate_vals['height_well'])
        elif crop_top_left[0] < width / 2 and crop_top_left[1] < height / 2:
            if True:
                print("Top left")
            # top left --> bottom left of bounding box is defined by lower bottom and raised left
            robot_ref_point = self.converter.pixelToRobot(ref_point, self.converter.checkerboard_z + wellplate_vals['height_top'])
            robot_ref_point2 = (robot_ref_point[0], robot_ref_point[1], robot_ref_point[2] - wellplate_vals['height_top'])
            ref_point2 = self.converter.robotToPixel(robot_ref_point2)
            bottom_left = (ref_point2[0], ref_point[1])
            robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
            robot_a1 = (robot_bottom_left[0] + wellplate_vals['welloffset_x'],
                        robot_bottom_left[1] + wellplate_vals['welloffset_y'],
                        robot_bottom_left[2] + wellplate_vals['height_well'])

        a1_pixel = self.converter.robotToPixel(robot_a1)
        if debug:
            print("robot ref point: {}".format(robot_ref_point))
            print("robot a1: {}".format(robot_a1))
            print("a1 pixel: {}".format(a1_pixel))
            cv2.circle(image, a1_pixel, 3, (255, 255, 0), -1)
            cv2.circle(image, a1_pixel2, 3, (0, 255, 255), -1)

            cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),1)

            cv2.imshow("thresh", thresh)
            cv2.imshow("cropped image", cropped_image)
            cv2.waitKey(0)

        robot_ref_point = self.converter.pixelToRobot(ref_point, self.converter.checkerboard_z)
        # return robot_ref_point
        return robot_a1

    def find_point_coordinates(self, object_type, box, image, debug=False):
        height, width, _ = image.shape
        midx = int((box[1] + box[3]) * width / 2)
        midy = int((box[0] + box[2]) * height / 2)
        robot_point = self.converter.pixelToRobot((midx, midy), self.converter.checkerboard_z + self.measurements[object_type]['height'])
        if debug:
            print(robot_point)
            cv2.circle(image, (midx, midy), 3, (120, 120, 0), 2)
            cv2.imshow("image", image)
            cv2.waitKey(0)

        return robot_point


if __name__ == "__main__":
    img = cv2.imread('../calibration/checkerboard_images/img21.jpg')
    ft = FineTuner(img, debug=True)
    print(ft.converter.robot_to_obj_mtx)
    print(ft.converter.obj_to_robot_mtx)