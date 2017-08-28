import cv2
from inspect import getsourcefile
from os.path import abspath, join, dirname
from RobotCoordinateConverter import RobotCoordinateConverter

class FineTuner:


    # look in OT code to find measured offsets between wells
    measurements = {'tiprack-200ul' : {'space' : 9, 'top_width' : 76, 'top_length' : 120, 'welloffset_x' : 6.5, 'welloffset_y' : 11, 'height_green' : 54, 'height_tip' : 64.5}}

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
        if object_type == "tiprack-200ul":
            coordinates = self.find_tiprack_a1(box, image)
        # height, width, _ = image.shape
        # cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        # cv2.imshow("item", cropped_image)
        # cv2.waitKey(0)
        return 'test'

    def find_tiprack_a1(self, box, image):
        height, width, _ = image.shape
        crop_top_left = (int(box[1] * width - 10), int(box[0] * height - 10))
        cropped_image = image[int(box[0] * height - 10):int(box[2] * height + 10), int(width * box[1] - 10):int(width * box[3] + 10)]
        cropped_height, cropped_width, _ = cropped_image.shape
        frame_to_thresh = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(frame_to_thresh, (58, 67, 0), (78, 255, 255))
        _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(cropped_image, contours, -1, (0,255,0), 3)
        for cnt in contours:
            if cv2.contourArea(cnt) > cropped_height * cropped_width / 2:
                x,y,w,h = cv2.boundingRect(cnt)
                # A1 is bottom left
                bottom_left = (x + crop_top_left[0], y + h + crop_top_left[1])
                print("Bottom left: {}".format(bottom_left))
                # Need to pass in pixel values in relation to the entire image
                tiprack_vals = self.measurements['tiprack-200ul']
                robot_bottom_left = self.converter.pixelToRobot(bottom_left, self.converter.checkerboard_z + tiprack_vals['height_green'])
                print(robot_bottom_left.shape)
                print("Robot bottom left: {}".format(robot_bottom_left))
                # TODO: make pixelToRobot return tuple
                robot_a1 =  (robot_bottom_left[0][0] + tiprack_vals['welloffset_x'], robot_bottom_left[1][0] + tiprack_vals['welloffset_y'], self.converter.checkerboard_z + tiprack_vals['height_tip'])
                robot_top_left = ((robot_bottom_left[0][0] + tiprack_vals['top_width'], robot_bottom_left[1][0] + tiprack_vals['top_length'], robot_bottom_left[2][0]))
                print("Robot a1: {}".format(robot_a1))
                print("Robot top left: {}".format(robot_top_left))
                a1 = self.converter.robotToPixel(robot_a1)
                topleft = self.converter.robotToPixel(robot_top_left)
                print("a1: {}".format(a1))
                print("topleft: {}".format(topleft))
                cv2.line(image, bottom_left, topleft, (0, 0, 255), 2)
                cv2.circle(image, a1, 3, (255, 0, 0), 2)
                #cv2.rectangle(cropped_image,(x,y),(x+w,y+h),(0,255,0),2)

        cv2.imshow("tiprack", thresh)
        cv2.imshow("cropped image", cropped_image)
        cv2.waitKey(0)
        return None


if __name__ == "__main__":
    img = cv2.imread('../calibration/checkerboard_images/img21.jpg')
    ft = FineTuner(img)
    print(ft.converter.robot_to_obj_mtx)
    print(ft.converter.obj_to_robot_mtx)