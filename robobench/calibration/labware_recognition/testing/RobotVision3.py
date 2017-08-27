import cv2
import imutils
import ObjectDetector2
import FineTuner
import time
from inspect import getsourcefile
from os.path import abspath, join, dirname

class RobotVision:

    def __init__(self, camera=None):
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
        self.object_detector = ObjectDetector2.ObjectDetector(self.num_classes, self.ckpt_path, self.label_path)
        self.deck_roi = []
        # TODO: remove, for testing
        #frame = cv2.imread(join(self.absolute_dir_path,'../calibration/checkerboard_images/img21.jpg'))
        path = join(self.absolute_dir_path, "VisionTestingImages/checkerboardimg1")
        print(path)
        frame = cv2.imread(join(self.absolute_dir_path, "VisionTestingImages/checkerboardimg1.jpg"))
        # self.select_deck_roi(frame)
        self.deck_dimensions = (5, 3)
        self.resize_width = 1000
        # _, frame = self.camera.read()
        # frame = imutils.resize(frame, width=self.resize_width)
        self.select_deck_roi(frame)
        self.fine_tune_calibrator = FineTuner.FineTuner(frame)


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
        cv2.namedWindow('Set crop')
        cv2.imshow('Set crop', frame)
        cv2.setMouseCallback('Set crop', self.get_roi, self.deck_roi)
        cv2.waitKey(0)
        print(self.deck_roi)
        cv2.destroyWindow('Set crop')

    def boxes_map_to_slots_map(self, name_to_boxes_map, frame):
        '''
        Generates name_to_slots_boxes_map based on name_to_boxes_map, self.deck_dimensions and self.deck_roi
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

                print("midx: {}".format(midx))
                print(self.deck_dimensions[0] * midx)
                letter = chr(ord('A') + int(self.deck_dimensions[0] * midx))
                number = self.deck_dimensions[1] - int(self.deck_dimensions[1] * midy)
                slot = letter + str(number)
                #TODO: is copy needed of box? Any chance ref is changed?
                slot_list.append((slot, box))

            name_to_slots_boxes_map[name] = slot_list

        return name_to_slots_boxes_map

    def generate_coordinate_map(self, name_to_slots_boxes_map, frame):
        '''
        Generate names_to_slots_coordinates_map mapping {item type: [(slot, robot coordinates for calibration)]} from
        names_to_slots_boxes_map
        '''
        name_to_slots_coordinates_map = {}
        for name, slot_boxes in name_to_slots_boxes_map.items():
            position_list = []
            for slot_box in slot_boxes:
                calibration_coordinates = self.fine_tune_calibrator.get_calibration_coordinates(name, slot_box[1], frame)
                position_list.append((slot_box[1], calibration_coordinates))
            name_to_slots_coordinates_map[name] = position_list

        return name_to_slots_coordinates_map



    def evaluate_deck(self, frame=None):
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
        if len(self.deck_roi) == 2:
            print("Passing in crop {}".format(self.deck_roi))
            name_to_boxes_map = self.object_detector.detect(frame, self.deck_roi)
        else: 
            name_to_boxes_map = self.object_detector.detect(frame)
        print(name_to_boxes_map)
        name_to_slots_boxes_map = self.boxes_map_to_slots_map(name_to_boxes_map, frame)
        name_to_slots_coordinates_map = self.generate_coordinate_map(name_to_slots_boxes_map, frame)
        print(name_to_slots_boxes_map)
        print(name_to_slots_coordinates_map)
        cv2.imshow("Detected", frame)
        cv2.waitKey(0)

if __name__ == "__main__":
    vis = RobotVision()
    frame = cv2.imread(join(vis.absolute_dir_path, "VisionTestingImages/wellplateB2E1.jpg"))
    vis.evaluate_deck(frame)
    #print(vis.fine_tune_calibrator.converter.obj_to_robot_mtx)



