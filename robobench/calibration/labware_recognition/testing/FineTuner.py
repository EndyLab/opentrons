import cv2
from inspect import getsourcefile
from os.path import abspath, join, dirname
from RobotCoordinateConverter import RobotCoordinateConverter
import numpy as np
import math

class FineTuner:


    # TODO: look in OT code to find measured offsets between wells
    # TODO: remeasure values using robot? Currently assuming robot mm is accurate
    # TODO: measure point values properly
    # tiprack offset x 10, y 14 initially
    # (51, 315) --> (40.5, 301)
    measurements = {# 'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 8, 'welloffset_y' : 7, 'height_green' : 54, 'height_tip' : 64.5, 'tip_offset' : 54.5},
                    'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 7, 'welloffset_y' : 5, 'height_green' : 54, 'height_tip' : 64.5, 'tip_offset' : 54.5},
                    'WellPlate' : {'height_well' : 0, 'height_top': 11, 'welloffset_x' : 10.5, 'welloffset_y' : 10, 'length' : 127.33, 'width' : 85},
                    'Trash' : {'height': 50},
                    'Scale' : {'height' : 22},
                    'Trough' : {'height': 20}
                    }

    def __init__(self, calibration_img, debug=False):
        # Initialize coordinate converter
        # Assign classes to analysis functions
        self.converter = RobotCoordinateConverter()
        self.converter.calibrate(calibration_img, debug)
        pass

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
        # height, width, _ = image.shape
        # cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        # cv2.imshow("item", cropped_image)
        # cv2.waitKey(0)
        return coordinates

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
        box = np.int0(box)
        print(box)
        left_to_right = sorted(box, key=lambda x: x[0])
        print(left_to_right)
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

        robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
        robot_bottom_right = self.converter.pixelToRobot(bottom_right, self.converter.checkerboard_z + tiprack_vals['height_green'])
        robot_top_left = self.converter.pixelToRobot(top_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
        bottom_offset = (robot_bottom_right[0] - robot_bottom_left[0], robot_bottom_right[1] - robot_bottom_left[1])
        bottom_dist = math.sqrt(bottom_offset[0] ** 2 + bottom_offset[1] ** 2)
        left_offset = (robot_top_left[0] - robot_bottom_left[0], robot_top_left[1] - robot_bottom_left[1])
        left_dist = math.sqrt(left_offset[0] ** 2 + left_offset[1] ** 2)
        # print("robot_bottom_left: {}".format(robot_bottom_left))
        # print("robot_bottom_right: {}".format(robot_bottom_right))
        # print("robot_top_left: {}".format(robot_top_left))
        # print("left_offset: {}".format(left_offset))
        # print("bottom offset: {}".format(bottom_offset))
        # print("bottom dist: {}".format(bottom_dist))
        # print("left_dist: {}".format(left_dist))

        displace_x = left_offset[0]  / left_dist * tiprack_vals['welloffset_y'] + bottom_offset[0] / bottom_dist * tiprack_vals['welloffset_x']
        displace_y = left_offset[1]  / left_dist * tiprack_vals['welloffset_y'] + bottom_offset[1] / bottom_dist * tiprack_vals['welloffset_x']
        # print("disp x: {}".format(displace_x))
        # print("disp y: {}".format(displace_y))

        robot_a1 = (robot_bottom_left[0] + displace_x, robot_bottom_left[1] + displace_y, -31)
        return robot_a1


        # x,y,w,h = cv2.boundingRect(max_contour)
        # # A1 is bottom left
        # bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
        
        # # Need to pass in pixel values in relation to the entire image
        # tiprack_vals = self.measurements['tiprack-200ul']
        # robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
        
        # robot_a1 =  (robot_bottom_left[0] + tiprack_vals['welloffset_x'], robot_bottom_left[1] + tiprack_vals['welloffset_y'], self.converter.checkerboard_z + tiprack_vals['height_tip'])
        # robot_top_left = ((robot_bottom_left[0] + tiprack_vals['top_width'], robot_bottom_left[1] + tiprack_vals['top_length'], robot_bottom_left[2]))
        
        # a1 = self.converter.robotToPixel(robot_a1)
        # topleft = self.converter.robotToPixel(robot_top_left)
        
        # if debug:
        #     print("Bottom left: {}".format(bottom_left))
        #     print("Robot bottom left: {}".format(robot_bottom_left))
        #     print("Robot a1: {}".format(robot_a1))
        #     print("Robot top left: {}".format(robot_top_left))
        #     print("a1: {}".format(a1))
        #     print("topleft: {}".format(topleft))

        #     cv2.line(image, bottom_left, topleft, (0, 0, 255), 2)
        #     cv2.circle(image, a1, 3, (255, 0, 0), 2)
        #     cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),2)

        #     cv2.imshow("tiprack", thresh)
        #     cv2.imshow("cropped image", cropped_image)
        #     cv2.waitKey(0)
        # robot_a1 = (robot_a1[0], robot_a1[1], robot_a1[2] - tiprack_vals['tip_offset'])
        # return robot_a1

        # for cnt in contours:
        #     # TODO: limit to largest contour? Though there should only be 1 this large
        #     if cv2.contourArea(cnt) > cropped_height * cropped_width / 2:
                # x,y,w,h = cv2.boundingRect(cnt)
                # # A1 is bottom left
                # bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
                # print("Bottom left: {}".format(bottom_left))
                # # Need to pass in pixel values in relation to the entire image
                # tiprack_vals = self.measurements['tiprack-200ul']
                # robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
                # print("Robot bottom left: {}".format(robot_bottom_left))
                # robot_a1 =  (robot_bottom_left[0] + tiprack_vals['welloffset_x'], robot_bottom_left[1] + tiprack_vals['welloffset_y'], self.converter.checkerboard_z + tiprack_vals['height_tip'])
                # robot_top_left = ((robot_bottom_left[0] + tiprack_vals['top_width'], robot_bottom_left[1] + tiprack_vals['top_length'], robot_bottom_left[2]))
                # print("Robot a1: {}".format(robot_a1))
                # print("Robot top left: {}".format(robot_top_left))
                # a1 = self.converter.robotToPixel(robot_a1)
                # topleft = self.converter.robotToPixel(robot_top_left)
                # print("a1: {}".format(a1))
                # print("topleft: {}".format(topleft))
                # cv2.line(image, bottom_left, topleft, (0, 0, 255), 2)
                # cv2.circle(image, a1, 3, (255, 0, 0), 2)
                # #cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),2)

    def find_wellplate_a1(self, box, image, debug=False):
        height, width, _ = image.shape
        crop_top_left = (int(box[1] * width - 10), int(box[0] * height - 10))
        cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        cropped_height, cropped_width, _ = cropped_image.shape
        frame_to_thresh = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(frame_to_thresh, (0, 0, 165), (255, 255, 255))
        # night time, need to generalize to work in different conditions
        # thresh = cv2.inRange(frame_to_thresh, (0, 0, 100), (255, 255, 255))
        if debug:
            cv2.imshow("thresh", thresh)
            cv2.waitKey(0)
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key=lambda x: cv2.contourArea(x))
        rect = cv2.minAreaRect(max_contour)
        
        x,y,w,h = cv2.boundingRect(max_contour)
        wellplate_vals = self.measurements['WellPlate']
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
                        robot_ref_point[2] +  - wellplate_vals['height_top'] + wellplate_vals['height_well'])
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

        ##############################################################

        # if crop_top_left[0] > width / 2:
        #     right = 1
        # else:
        #     right = 0
        # if crop_top_left[1] > height / 2:
        #     bottom = 1
        #     top = 0
        # else:
        #     bottom = 0
        #     top = 1

        # ref_point = (x + crop_top_left[0] + right * w, y + crop_top_left[1] + bottom * h)
        # robot_ref_point = self.converter.pixelToRobot(ref_point, self.converter.checkerboard_z)
        # robot_a1 = (robot_ref_point[0] - right * wellplate_vals['width'] + wellplate_vals['welloffset_x'],
        #             robot_ref_point[1] - top * wellplate_vals['length'] + wellplate_vals['welloffset_y'],
        #             robot_ref_point[2] + wellplate_vals['height'])
        # a1_pixel = self.converter.robotToPixel(robot_a1)
        # print("right: {}".format(right))
        # print("bottom: {}".format(bottom))
        # print("ref point: {}".format(ref_point))
        # print("robot_ref_point: {}".format(robot_ref_point))
        # print("robot a1: {}".format(robot_a1))
        # print("a1 pixel: {}".format(a1_pixel))
        # cv2.circle(image, a1_pixel, 3, (255, 0, 0), 1)
        # cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),1)

        # if crop_top_left[0] > width / 2:
        #     if crop_top_left[1] > height / 2:
        #         # bottom right
        #         top_left = (x + crop_top_left[0], y + crop_top_left[1])
        #         robot_top_left = self.converter.pixelToRobot(top_left, self.converter.checkerboard_z)
        #         robot_a1 = (robot_top_left[0] + wellplate_vals['welloffset_x'], robot_top_left[1] - wellplate_vals['length'] + wellplate_vals['welloffset_y'], robot_top_left[2] + wellplate_vals['height'])
        #         pass
        #     else:
        #         # top right
        #         bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
        #         robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
        #         robot_a1 = (robot_bottom_left[0] + wellplate_vals['welloffset_x'], robot_bottom_left[1] - wellplate_vals['welloffset_y'], robot_top_left[2] + wellplate_vals['height'])
        #         pass
        # else:
        #     if crop_top_left[1] > height / 2:
        #         # bottom left
        #         top_right = (x + w + crop_top_left[0], y + crop_top_left[1])
        #         robot_top_right = self.converter.pixelToRobot(top_right, self.converter.checkerboard_z)
        #         pass
        #     else:
        #         # top left
        #         bottom_right = (x + w + crop_top_left[0], y + h + crop_top_left[1])
        #         robot_bottom_right = self.converter.pixelToRobot(bottom_right, self.converter.checkerboard_z)
        #         pass
        # # A1 is bottom left
        # box_bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
        # print("Bottom left: {}".format(box_bottom_left))
        # robot_box_bottom_left = self.converter.pixelToRobot(box_bottom_left, self.converter.checkerboard_z)
        # print("Robot box bottom left: {}".format(robot_box_bottom_left))
        # # Need to pass in pixel values in relation to the entire image
        # wellplate_vals = self.measurements['WellPlate']


        # top_right = (x + crop_top_left[0] + w, y + crop_top_left[1])
        # print("Top right: {}".format(top_right))
        # robot_top_right = self.converter.pixelToRobot(top_right, self.converter.checkerboard_z)
        # print("Robot top right: {}".format(robot_top_right))
        # robot_a1 = (robot_top_right[0] - wellplate_vals['width'] + wellplate_vals['welloffset_x'], robot_top_right[1] - wellplate_vals['length'] + wellplate_vals['welloffset_y'],
        #                 self.converter.checkerboard_z + wellplate_vals['height'])
        # robot_bottom_left = (robot_top_right[0] - wellplate_vals['width'], robot_top_right[1] - wellplate_vals['length'], robot_top_right[2])
        # a1 = self.converter.robotToPixel(robot_a1)
        # bottom_left = self.converter.robotToPixel(robot_bottom_left)
        # print("a1: {}".format(a1))
        # print("bottomleft: {}".format(bottom_left))
        # cv2.rectangle(image, bottom_left, top_right, (0, 0, 255), 1)
        # cv2.circle(image, a1, 3, (255, 0, 0), 1)
        # cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),1)


        # robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
        # print("Robot bottom left: {}".format(robot_bottom_left))
        # robot_a1 =  (robot_bottom_left[0] + wellplate_vals['welloffset_x'], robot_bottom_left[1] + wellplate_vals['welloffset_y'], self.converter.checkerboard_z + wellplate_vals['height'])
        # robot_top_right = ((robot_bottom_left[0] + wellplate_vals['width'], robot_bottom_left[1] + wellplate_vals['length'], robot_bottom_left[2]))
        # print("Robot a1: {}".format(robot_a1))
        # print("Robot top right: {}".format(robot_top_left))
        # a1 = self.converter.robotToPixel(robot_a1)
        # topleft = self.converter.robotToPixel(robot_top_left)
        # print("a1: {}".format(a1))
        # print("topleft: {}".format(topleft))
        # cv2.line(image, bottom_left, topleft, (0, 0, 255), 1)
        # cv2.circle(image, a1, 3, (255, 0, 0), 1)
        # cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),1)
        # for cnt in contours:
        #     if cv2.contourArea(cnt) > cropped_height * cropped_width / 2:
        #         x,y,w,h = cv2.boundingRect(cnt)
        #         # A1 is bottom left
        #         bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
        #         print("Bottom left: {}".format(bottom_left))
        #         # Need to pass in pixel values in relation to the entire image
        #         wellplate_vals = self.measurements['WellPlate']
        #         robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
        #         print("Robot bottom left: {}".format(robot_bottom_left))
        #         robot_a1 =  (robot_bottom_left[0] + wellplate_vals['welloffset_x'], robot_bottom_left[1] + wellplate_vals['welloffset_y'], self.converter.checkerboard_z + wellplate_vals['height'])
        #         robot_top_left = ((robot_bottom_left[0] + wellplate_vals['width'], robot_bottom_left[1] + wellplate_vals['length'], robot_bottom_left[2]))
        #         print("Robot a1: {}".format(robot_a1))
        #         print("Robot top left: {}".format(robot_top_left))
        #         a1 = self.converter.robotToPixel(robot_a1)
        #         topleft = self.converter.robotToPixel(robot_top_left)
        #         print("a1: {}".format(a1))
        #         print("topleft: {}".format(topleft))
        #         cv2.line(image, bottom_left, topleft, (0, 0, 255), 1)
        #         cv2.circle(image, a1, 3, (255, 0, 0), 1)
        #         cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),1)
                # rect = cv2.minAreaRect(cnt)
                # print(rect)
                # # print(type(rect))
                # box = cv2.boxPoints(rect)
                # box = np.int0(box)
                # print(box)
                # cv2.drawContours(cropped_image,[box],0,(0,0,255),2)
                # wellplate_vals = self.measurements['WellPlate']
                # # TODO: not guaranteed same ordering, check manually
                # bottom_left = (box[0][0] + crop_top_left[0], box[0][1] + crop_top_left[1])
                # print("Bottom left: {}".format(bottom_left))
                # robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
                # robot_top_right = (robot_bottom_left[0] + wellplate_vals['width'], robot_bottom_left[1] + wellplate_vals['length'], robot_bottom_left[2])
                # print("Robot bottom left: {}".format(robot_bottom_left))
                # print("Robot top right: {}".format(robot_top_right))
                # top_right = self.converter.robotToPixel(robot_top_right)
                # print("Top right: {}".format(top_right))
                # cv2.line(image, bottom_left, top_right, (0, 150, 150), 2)

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
    ft = FineTuner(img)
    print(ft.converter.robot_to_obj_mtx)
    print(ft.converter.obj_to_robot_mtx)