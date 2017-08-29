import cv2
from inspect import getsourcefile
from os.path import abspath, join, dirname
from RobotCoordinateConverter import RobotCoordinateConverter
import numpy as np

class FineTuner:


    # TODO: look in OT code to find measured offsets between wells
    # TODO: remeasure values using robot? Currently assuming robot mm is accurate
    # TODO: measure point values properly
    measurements = {'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 10, 'welloffset_y' : 14, 'height_green' : 54, 'height_tip' : 64.5, 'tip_offset' : 54.5},
                    'WellPlate' : {'height' : 14, 'welloffset_x' : 10, 'welloffset_y' : 10, 'length' : 127.33, 'width' : 85},
                    'Trash' : {'height': 50},
                    'Scale' : {'height' : 22},
                    'Trough' : {'height': 20}
                    }

    def __init__(self, calibration_img):
        # Initialize coordinate converter
        # Assign classes to analysis functions
        self.converter = RobotCoordinateConverter()
        self.converter.calibrate(calibration_img)
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
        if object_type == "TipRack":
            coordinates = self.find_tiprack_a1(box, image)
        elif object_type == "WellPlate":
            coordinates = self.find_wellplate_a1(box, image)
        elif object_type == "Trash" or object_type == "Trough" or object_type == "Scale":
            coordinates = self.find_point_coordinates(object_type, box, image)
        else:
            coordinates = 'Unknown object'
        # height, width, _ = image.shape
        # cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        # cv2.imshow("item", cropped_image)
        # cv2.waitKey(0)
        return coordinates

    def find_tiprack_a1(self, box, image):
        height, width, _ = image.shape
        crop_top_left = (int(box[1] * width - 10), int(box[0] * height - 10))
        cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        cropped_height, cropped_width, _ = cropped_image.shape
        frame_to_thresh = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(frame_to_thresh, (58, 67, 0), (78, 255, 255))
        cv2.imshow("thresh", thresh)
        #cv2.waitKey(0)
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key=lambda x: cv2.contourArea(x))
        cv2.drawContours(cropped_image, [max_contour], -1, (0,255,0), 3)
        cv2.imshow("Contours", cropped_image)
        x,y,w,h = cv2.boundingRect(max_contour)
        # A1 is bottom left
        bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
        print("Bottom left: {}".format(bottom_left))
        # Need to pass in pixel values in relation to the entire image
        tiprack_vals = self.measurements['tiprack-200ul']
        robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
        print("Robot bottom left: {}".format(robot_bottom_left))
        robot_a1 =  (robot_bottom_left[0] + tiprack_vals['welloffset_x'], robot_bottom_left[1] + tiprack_vals['welloffset_y'], self.converter.checkerboard_z + tiprack_vals['height_tip'])
        robot_top_left = ((robot_bottom_left[0] + tiprack_vals['top_width'], robot_bottom_left[1] + tiprack_vals['top_length'], robot_bottom_left[2]))
        print("Robot a1: {}".format(robot_a1))
        print("Robot top left: {}".format(robot_top_left))
        a1 = self.converter.robotToPixel(robot_a1)
        topleft = self.converter.robotToPixel(robot_top_left)
        print("a1: {}".format(a1))
        print("topleft: {}".format(topleft))
        cv2.line(image, bottom_left, topleft, (0, 0, 255), 2)
        cv2.circle(image, a1, 3, (255, 0, 0), 2)
        #cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),2)

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

        cv2.imshow("tiprack", thresh)
        cv2.imshow("cropped image", cropped_image)
        #cv2.waitKey(0)
        robot_a1 = (robot_a1[0], robot_a1[1], robot_a1[2] - tiprack_vals['tip_offset'])
        return robot_a1


    def find_wellplate_a1(self, box, image):
        height, width, _ = image.shape
        crop_top_left = (int(box[1] * width - 10), int(box[0] * height - 10))
        cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        cropped_height, cropped_width, _ = cropped_image.shape
        frame_to_thresh = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(frame_to_thresh, (0, 0, 165), (255, 255, 255))
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > cropped_height * cropped_width / 2:
                x,y,w,h = cv2.boundingRect(cnt)
                # A1 is bottom left
                bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
                print("Bottom left: {}".format(bottom_left))
                # Need to pass in pixel values in relation to the entire image
                wellplate_vals = self.measurements['WellPlate']
                robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z)
                print("Robot bottom left: {}".format(robot_bottom_left))
                robot_a1 =  (robot_bottom_left[0] + wellplate_vals['welloffset_x'], robot_bottom_left[1] + wellplate_vals['welloffset_y'], self.converter.checkerboard_z + wellplate_vals['height'])
                robot_top_left = ((robot_bottom_left[0] + wellplate_vals['width'], robot_bottom_left[1] + wellplate_vals['length'], robot_bottom_left[2]))
                print("Robot a1: {}".format(robot_a1))
                print("Robot top left: {}".format(robot_top_left))
                a1 = self.converter.robotToPixel(robot_a1)
                topleft = self.converter.robotToPixel(robot_top_left)
                print("a1: {}".format(a1))
                print("topleft: {}".format(topleft))
                cv2.line(image, bottom_left, topleft, (0, 0, 255), 2)
                cv2.circle(image, a1, 3, (255, 0, 0), 2)
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

        cv2.imshow("thresh", thresh)
        cv2.imshow("cropped image", cropped_image)
        #cv2.waitKey(0)
        return "Not implemented yet"

    def find_point_coordinates(self, object_type, box, image):
        height, width, _ = image.shape
        midx = int((box[1] + box[3]) * width / 2)
        midy = int((box[0] + box[2]) * height / 2)
        robot_point = self.converter.pixelToRobot((midx, midy), self.converter.checkerboard_z + self.measurements[object_type]['height'])
        print(robot_point)
        cv2.circle(image, (midx, midy), 3, (120, 120, 0), 2)
        cv2.imshow("image", image)
        #cv2.waitKey(0)
        return robot_point


if __name__ == "__main__":
    img = cv2.imread('../calibration/checkerboard_images/img21.jpg')
    ft = FineTuner(img)
    print(ft.converter.robot_to_obj_mtx)
    print(ft.converter.obj_to_robot_mtx)