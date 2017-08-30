import cv2
import numpy as np
from skimage import exposure
from imutils import contours
from imutils import perspective
import imutils
import glob, os
from PIL import Image
from bradley_thresh import faster_bradley_threshold
from classify import knn
import json
from datetime import datetime

def enhance_screen_thresh(img):
    cv2.imshow("screen", img)
    cv2.waitKey(0)
    
    kernel = np.ones((21,21),np.uint8)
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    cv2.imshow("screen", closing)
    cv2.waitKey(0)
    return closing


# crops the screen and saves it
def extract_screen(img, file):
    # filters hsv to get screen
    hsv_threshed = color_filter(img)
    hsv_threshed = enhance_screen_thresh(hsv_threshed)

    # gets contour points of screen
    pts = getScreen(hsv_threshed)

    # extracts screen from origional image
    if len(pts) != 0:
        screen = perspective.four_point_transform(img, pts)
        cv2.imwrite(r'C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/flat_camera/crops/'+file, screen)
        return 0
    else:
        return -1


# uses hsv blue filtering to isolate the screen
def color_filter(img):
    BLUE_MIN = np.array([50, 150, 245],np.uint8)
    BLUE_MAX = np.array([120, 255, 255],np.uint8)

    hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    res = cv2.inRange(hsv_img, BLUE_MIN, BLUE_MAX)
    # cv2.imshow("screen", res)
    # cv2.waitKey(0)
    return res

# gets the screen coords
def getScreen(img):
    img3, contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
    windowH, windowW = img.shape
    window_area = windowW*windowH
    screenContour = None

    #  largest contour
    peri = cv2.arcLength(contours[0], True)
    approx = cv2.approxPolyDP(contours[0], 0.10 * peri, True)
    color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
    cv2.drawContours(color,approx,-1,(0,0,255),3)
    cv2.imshow("contours", color)
    cv2.waitKey(0)

    pts = get_points(approx)

    try:
        len(pts)
        return pts
    except TypeError:
        return []

    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # if our approximated contour has four points, then we can assume that we have found our screen
        area = cv2.contourArea(approx)
        # print("screen area", float(area/window_area))
        if len(approx) == 4:
            color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
            cv2.drawContours(color,approx,-1,(0,0,255),3)
            # cv2.imshow("contours", color)
            # cv2.waitKey(0)
            screenContour = approx
            break

    pts = get_points(screenContour)

    try:
        len(pts)
        return pts
    except TypeError:
        return []

# returns contour points in a more usbale form
def get_points(contourPoints):
    x = []
    y = []
    if len(contourPoints) < 4:
        return
    try:
        for point in contourPoints:
            coord = point[0]
            x.append(coord[0])
            y.append(coord[1])
            # print(coord)

        # print("x:", x,"y:",y)
        pts = np.array([(x[0], y[0]), (x[1], y[1]), (x[2], y[2]), (x[3], y[3])])
        # print(pts)
        return pts
    except TypeError:
        return


