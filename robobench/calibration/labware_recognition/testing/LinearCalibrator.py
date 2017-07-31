import os
import cv2
import ObjectDetector
import numpy as np

IMAGE_PATH = 'VOCdevkit/LabImages_Cropped/JPEGImages/labimage204cropped.jpg'
DECK_REF_POINTS = [(31.85,396.0), (362.65, 112.0)]
img_points = []



class LinearCalibrator:
    def __init__(self, img_path=IMAGE_PATH, deck_ref_points=DECK_REF_POINTS):
        self.img_points = []
        self.deck_ref_points = deck_ref_points
        self.img_path = img_path
        self.img = None
        cv2.namedWindow(img_path)
        
     
    def build_reference(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            if (len(self.img_points) > 1):
                self.img_points.pop(0)
            self.img_points.append((x,y))
            print(self.img_points)
        
    def do_nothing(self, event, x, y, flags, param):
        return
    
    def destroyWindow(self):
        cv2.destroyWindow(self.img_path)

    def calibrate(self):  
        cv2.setMouseCallback(self.img_path, self.build_reference)
        self.img = cv2.imread(self.img_path)
        cv2.imshow(self.img_path, self.img)
        cv2.waitKey(0) 
        cv2.setMouseCallback(self.img_path, self.do_nothing)
    
    def transform(self, coord, dim):
        return (coord - self.img_points[0][dim]) / (self.img_points[1][dim] - self.img_points[0][dim]) * (self.deck_ref_points[1][dim] - self.deck_ref_points[0][dim]) + self.deck_ref_points[0][dim]

    def evaluate(self):
        if len(self.img_points) != 2:
            return {'error': 'Must calibrate before evaluation'}
        # Each box is (ymin, xmin, ymax, xmax)
        pos_dict = ObjectDetector.detect(img_path=self.img_path)
        if len(pos_dict) != 1:
            return {'error':'{} objects detected'.format(len(pos_dict))}
        else:
            labware, position = list(pos_dict.items())[0]
            height, width = self.img.shape[:2]
            # xmin * width, ymax * height
            x = self.transform(width * position[1], 0)
            y = self.transform(height * position[2], 1)
            name, percentage = [c.strip() for c in labware.split(':')]
            return {'item':name, 'x':x, 'y':y, 'percent':percentage}
            # return '{} ({}, {})'.format(labware, x, y)
 
if __name__ == "__main__":
    c = LinearCalibrator()
    c.calibrate()
    print(c.evaluate())
    c.destroyWindow()