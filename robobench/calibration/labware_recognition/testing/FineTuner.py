import cv2
from inspect import getsourcefile
from os.path import abspath, join, dirname
from RobotCoordinateConverter import RobotCoordinateConverter

class FineTuner:

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
        height, width, _ = image.shape
        cropped_image = image[int(box[0] * height):int(box[2] * height), int(width * box[1]):int(width * box[3])]
        cv2.imshow("item", cropped_image)
        cv2.waitKey(0)
        return 'test'


if __name__ == "__main__":
    img = cv2.imread('../calibration/checkerboard_images/img21.jpg')
    ft = FineTuner(img)
    print(ft.converter.robot_to_obj_mtx)
    print(ft.converter.obj_to_robot_mtx)