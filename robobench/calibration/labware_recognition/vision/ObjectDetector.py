import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2

import collections

from inspect import getsourcefile
from os.path import abspath, join, dirname

from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

import glob
import time
import imutils

# This is needed since the model is stored in the object_detection folder.
absolute_dir_path = abspath(dirname(getsourcefile(lambda:0)))
sys.path.append(join(absolute_dir_path, "../models"))
sys.path.append(join(absolute_dir_path, "../models/object_detection"))

from utils import label_map_util
import calibration_visualization_utils as vis_utils

class ObjectDetector:

    def __init__(self, num_classes, graph_path, label_path):
        self.setGraph(num_classes, graph_path, label_path)

    def setGraph(self, num_classes, graph_path, label_path):
        '''
        Loads detection graph 
        Args:
            num_classes (int): number of classes in trained model to be used
            graph_path (str): path to frozen inference graph
            label_path (str): path to label map for trained model
        '''
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(graph_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
                self.label_map = label_map_util.load_labelmap(label_path)
                self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=num_classes, use_display_name=True)
                self.category_index = label_map_util.create_category_index(self.categories)
                self.sess = tf.Session(graph=self.detection_graph)

    def detect(self, image, deck_roi=None, debug=False):
        '''
        Detects objects in image and returns dictionary mapping 
        {object type:list of bounding boxes (ymin, xmin, ymax, xmax)}
        relative to uncropped image

        Args:
            image (cv2::Mat): image to be processed
            deck_roi (tuple, optional): bounding box to crop for deck in format ((xmin, ymin), (xmax, ymax)). Default None

        Returns:
            dict(str:list(box)): returns a dictionary mapping object types to a list of detected bounding boxes.
                                Box positions are normalized and formatted as (ymin, xmin, ymax, xmax)
        '''
        print(deck_roi)
        if deck_roi is not None:
            cropped_image = image[deck_roi[0][1]:deck_roi[1][1], deck_roi[0][0]:deck_roi[1][0]]
        else:
            cropped_image = image
            
        if debug:
            print(deck_roi)
            cv2.imshow("img to detect", cropped_image)
            cv2.waitKey(0)

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(cropped_image, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        # Actual detection.
        (boxes, scores, classes, num_detections) = self.sess.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})
        # Visualization of the results of a detection.
        output = vis_utils.visualize_boxes_and_labels_on_image_array(
            cropped_image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8)

        if deck_roi is not None:
            cropped_height, cropped_width, _ = cropped_image.shape
            full_height, full_width, _ = image.shape
            #print("Preadjustment boxes: {}".format(output))
            for item, boxes in output.items():
                for i in range(len(boxes)):
                    box = boxes[i]
                    # adjust normalized values to uncropped image
                    boxes[i] = ((box[0] * cropped_height + deck_roi[0][1]) / full_height, 
                            (box[1] * cropped_width + deck_roi[0][0]) / full_width,
                            (box[2] * cropped_height + deck_roi[0][1]) / full_height, 
                            (box[3] * cropped_width + deck_roi[0][0]) / full_width)

        #print("Final output: {}".format(output))

        return output


if __name__ == "__main__":
    detector = ObjectDetector(5, "../models/object_detection/TopViewPipeline/outputs/17806/frozen_inference_graph.pb", "../models/object_detection/TopViewPipeline/data/pascal_label_map_top.pbtxt")
    # img = cv2.imread("../models/object_detection/TopViewPipeline/VOCdevkit_top/VOC2012/JPEGImages/96wellplate_enzo_D3_t-0.jpg")
    # img2 = cv2.imread("../models/object_detection/TopViewPipeline/VOCdevkit_top/VOC2012/JPEGImages/96wellplate_enzo_D3_t-0.jpg")
    # print(detector.detect(img, ((50, 10), (1000, 1000))))
    # print(detector.detect(img2))
    # cv2.imshow("img", img)
    # cv2.imshow("img2", img2)
    # cv2.waitKey(0)
    # index = 0
    # images = glob.glob('../models/object_detection/TopViewPipeline/VOCdevkit_top/VOC2012/JPEGImages/*.jpg')
    # for file in images:
    #     img = cv2.imread(file)
    #     cv2.imshow("image", img)
    #     result = detector.detect(img)
    #     cv2.imwrite("DetectorTest2/" + str(index) + ".jpg", img)
    #     index = index + 1
    cam = cv2.VideoCapture(0)
    time.sleep(.25)

    _, frame = cam.read()
    detector.detect(frame)
    cv2.imshow("frame", frame)
    k = cv2.waitKey(0) & 0xFF
    # if k == 's':
    #     cv2.imwrite("/Users/michaelbereket/Desktop/PosterFigures/detect.jpg", frame)


