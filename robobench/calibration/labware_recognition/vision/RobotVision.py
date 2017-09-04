import cv2
import imutils
import ObjectDetector
import FineTuner
import RobotCoordinateConverter
import time
from inspect import getsourcefile
from os.path import abspath, join, dirname
import numpy as np

class RobotVision:

    def __init__(self, camera=None, debug=False):
        if camera == None:
            camera = cv2.VideoCapture(0)
            time.sleep(.25)
        self.camera = camera
        #TODO: not necessary when done testing
        self.absolute_dir_path = abspath(dirname(getsourcefile(lambda:0)))
        # TODO: determine whether these values should be passed in
        self.ckpt_path = join(self.absolute_dir_path, "../models/object_detection/TopViewPipeline/outputs/17806/frozen_inference_graph.pb")
        self.label_path = join(self.absolute_dir_path, "../models/object_detection/TopViewPipeline/data/pascal_label_map_top.pbtxt")
        self.num_classes = 5
        self.object_detector = ObjectDetector.ObjectDetector(self.num_classes, self.ckpt_path, self.label_path)
        self.deck_roi = []
        # TODO: remove, for testing
        #frame = cv2.imread(join(self.absolute_dir_path,'../calibration/checkerboard_images/img21.jpg'))
        path = join(self.absolute_dir_path, "images/testset1/checkerboard_img_w1000_0.jpg")
        print(path)
        frame = cv2.imread(path)
        self.converter = RobotCoordinateConverter.RobotCoordinateConverter()
        self.converter.calibrate(frame, debug)
        frame = self.converter.undistort(frame, debug)
        self.select_deck_roi(frame)
        self.deck_dimensions = (5, 3)
        self.resize_width = 1000
        # _, frame = self.camera.read()
        # frame = imutils.resize(frame, width=self.resize_width)
        # self.select_deck_roi(frame)
        # self.deck_roi = [(244, 102), (775, 512)] # [(207, 76), (795, 539)] checkerboard img 3
        self.fine_tune_calibrator = FineTuner.FineTuner(self.converter)


    def get_roi(self, event, x, y, flags, param):
        """
        TODO: have point sort itself, draw frame when cropping
        Mouse event handler
        Expects ROI drawn as rect from top left to bottom right
        Stores corner points in crop_points
        """
        roi = param
        if event == cv2.EVENT_LBUTTONDOWN:
            roi.clear()
            roi.append((x,y))
            print('down')
        elif event == cv2.EVENT_LBUTTONUP:
            roi.append((x,y))

            print('up')

        print(roi)

    def select_deck_roi(self, frame=None):
        """
        Opens window with passed in img and allows ROI to be drawn. Closes when key pressed
        """
        if frame is None:
            # TODO: don't assume read works
            _, frame = self.camera.read()
            frame = imutils.resize(frame, width=self.resize_width)
            frame = self.converter.undistort(frame)
        cv2.namedWindow('Set crop')
        cv2.imshow('Set crop', frame)
        cv2.setMouseCallback('Set crop', self.get_roi, self.deck_roi)
        cv2.waitKey(0)
        print(self.deck_roi)
        cv2.destroyWindow('Set crop')

    def boxes_map_to_slots_map(self, name_to_boxes_map, frame):
        '''
        Generates name_to_slots_boxes_map based on name_to_boxes_map, self.deck_dimensions and self.deck_roi
        Expects frame already undistorted
        '''
        name_to_slots_boxes_map = {}
        for name, boxes in name_to_boxes_map.items():
            slot_list = []
            for box in boxes:
                height, width, _ = frame.shape
                cv2.rectangle(frame, (int(width * box[1]), int(height * box[0])), (int(width * box[3]), int(height * box[2])), (0, 255, 0), 3)
                midx = (box[1] + box[3]) / 2
                midy = (box[0] + box[2]) /2
                #A1 bottom left, E3 top right
                if len(self.deck_roi) == 2:
                    cropw = self.deck_roi[1][0] - self.deck_roi[0][0]
                    croph = self.deck_roi[1][1] - self.deck_roi[0][1]
                    height, width, _ = frame.shape
                    midx = (midx * width - self.deck_roi[0][0]) / cropw
                    midy = (midy * height - self.deck_roi[0][1]) / croph

                # print("midx: {}".format(midx))
                # print(self.deck_dimensions[0] * midx)
                letter = chr(ord('A') + int(self.deck_dimensions[0] * midx))
                number = self.deck_dimensions[1] - int(self.deck_dimensions[1] * midy)
                slot = letter + str(number)
                #TODO: is copy needed of box? Any chance ref is changed?
                slot_list.append((slot, box))

            name_to_slots_boxes_map[name] = slot_list

        return name_to_slots_boxes_map

    def generate_coordinate_map(self, name_to_slots_boxes_map, frame, debug=False):
        '''
        Generate names_to_slots_coordinates_map mapping {item type: [(slot, robot coordinates for calibration)]} from
        names_to_slots_boxes_map
        Expects frame already undistorted
        '''
        name_to_slots_coordinates_map = {}
        for name, slot_boxes in name_to_slots_boxes_map.items():
            position_list = []
            for slot_box in slot_boxes:
                calibration_coordinates = self.fine_tune_calibrator.get_calibration_coordinates(name, slot_box[1], frame, debug)
                position_list.append((slot_box[0], calibration_coordinates))
            name_to_slots_coordinates_map[name] = position_list

        return name_to_slots_coordinates_map



    def evaluate_deck(self, frame=None, debug=False):
        '''
        Determines what objects are on the deck and returns a dictionary {object type: [(slot, robot coordinate positions)]}

        Args:
            frame(cv2::Mat, optional): image to evaluate, by default captures image from instance camera

        Returns:
            dictionary {object type (str): [(slot (str), robot coordinate positions(tuple))]}
        '''

        if frame is None:
            # TODO: don't assume read is successful
            _, frame = self.camera.read()
            frame = imutils.resize(frame, width=self.resize_width)
            frame = self.undistort(frame, debug)
        clean_frame = np.copy(frame)
        if len(self.deck_roi) == 2:
            # print("Passing in crop {}".format(self.deck_roi))
            name_to_boxes_map = self.object_detector.detect(frame, self.deck_roi)
        else: 
            name_to_boxes_map = self.object_detector.detect(frame)
        if debug:
            print(name_to_boxes_map)
        name_to_slots_boxes_map = self.boxes_map_to_slots_map(name_to_boxes_map, frame)

        name_to_slots_coordinates_map = self.generate_coordinate_map(name_to_slots_boxes_map, clean_frame, debug)
        if debug:
            print(name_to_slots_boxes_map)
            print("Name to slots coordinates map: {}".format(name_to_slots_coordinates_map))
            cv2.imshow("Detected", frame)
            k = cv2.waitKey(0) & 0xFF
            if k == ord('s'):
                cv2.imwrite("/Users/michaelbereket/Desktop/PosterFigures/detect.jpg", frame)
        return name_to_slots_coordinates_map

if __name__ == "__main__":
    vis = RobotVision(debug=True)
    frame = cv2.imread(join(vis.absolute_dir_path, "../testing/VisionTestingImages/tiptest2.jpg"))
    frame = vis.converter.undistort(frame, True)
    print(vis.evaluate_deck(frame, debug=True))
    #print(vis.fine_tune_calibrator.converter.obj_to_robot_mtx)



