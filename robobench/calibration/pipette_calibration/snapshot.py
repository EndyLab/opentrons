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

def get_points(contourPoints):
    x = []
    y = []
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

def draw_rect(img, contour):
    # bounding rectangle
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    # print("box points!!!:", box)
    box = np.int0(box)
    cv2.drawContours(img,[box],0,(0,0,255),4)
    return box

def toGray(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = exposure.rescale_intensity(img_gray, out_range = (0, 255))
    
    # cv2.imshow("gray",img_gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img_gray)

    # cv2.imshow("gray optimzed",cl1)
    return cl1

def find_top_left_point(rect_coords):
    # put everything in a list
    ordered = []
    pts = get_points(rect_coords)
    for p in pts:
        ordered.append(tuple(p))

    # sort ascending x
    # print("ordered", ordered)
    ordered.sort(key=lambda tup: tup[0])
    # print("after sort:", ordered)
    ordered = ordered[:2]

    # sort descending y
    ordered.sort(key=lambda tup: tup[1])
    # print("after sort:", ordered[0])

    return ordered[0]

def color_filter(img):
    BLUE_MIN = np.array([10, 50, 180],np.uint8)
    BLUE_MAX = np.array([140, 255, 255],np.uint8)

    hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    hsv_threshed = cv2.inRange(hsv_img, BLUE_MIN, BLUE_MAX)
    cv2.imshow('filtered', hsv_threshed)

    cv2.waitKey(0)
    cv2.destroyAllWindows()  

def getScreen(img):
    # cv2.imshow("passed img", img)
    img3, contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
    cv2.drawContours(color,contours,-1,(0,255,0),3)
    cv2.imshow("passed img", color)

    windowH, windowW = img.shape
    window_area = windowW*windowH
    screenContour = None
    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.01 * peri, True)

        # print(approx)
       
     
        # if our approximated contour has four points, then we can assume that we have found our screen
        area = cv2.contourArea(approx)
        # if len(approx) == 4 and area >= .10 * window_area and area <= .50 * window_area:
        if len(approx) == 4 and area <= .3*window_area and area >= .01*window_area:
            color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
            cv2.drawContours(color,approx,-1,(0,0,255),3)
            cv2.imshow("screen", color)
            screenContour = approx
            break
            """
            tl = find_top_left_point(approx)
            # print(tl)
            color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
            cv2.circle(color,(tl[0],tl[1]), 1, (0,0,255), -1)

            # cv2.imshow("circle", color)

            # print("color:", bin_img[tl[1]+1][tl[0]+1])
            if bin_img[tl[1]+1][tl[0]+1] != 255:
                screenContour = approx
                break
            """
    cv2.waitKey(0)
    cv2.destroyAllWindows()   
    return screenContour

def isolate_screen(img):
    b,g,r = cv2.split(img)
    # b = exposure.rescale_intensity(b, out_range = (0, 255))
    
    # cv2.imshow("gray",img_gray)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # cl1 = clahe.apply(b)

    cv2.imshow('blue channel', b)
    blur = cv2.GaussianBlur(b,(5,5),0)
    ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    cv2.imshow("adaptive threshold", adapt_thresh)
    cv2.imshow("otsu threshold", otsu_thresh)

    screenContour = getScreen(otsu_thresh)
    pts = get_points(screenContour)
    # print(pts)
    try:
        len(pts)
        return pts
    except TypeError:
        return [-1, -1, -1, -1]
    


    cv2.waitKey(0)
    cv2.destroyAllWindows()


def scale_to_digit(img, debug='off'):
    # img processing
    ratio = 1
    img = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)

    if debug=='on':
        print('resizing img')

    # turn img gray
    img_gray = toGray(img)

    if debug=='on':
        print('turning img gray')

    # adaptive threshold
    blur = cv2.GaussianBlur(img_gray,(5,5),0)
    ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    if debug == 'on':
        cv2.imshow("adaptive threshold", adapt_thresh)
        cv2.imshow("otsu threshold", otsu_thresh)

    if debug=='on':
        print('calculating img threshold')

    # get screen
    screenContour = getScreen(adapt_thresh)
    pts = get_points(screenContour)

    if debug=='on':
        print('trying to find screen')

    # get digits
    try:
        len(pts)
        if debug=='on':
            print('found screen')
        box = img.copy()
        rect_pts = draw_rect(box, screenContour)
        screen = perspective.four_point_transform(img, rect_pts)

        if debug == 'on':
            cv2.imshow("detected screen", box)
        
        # binarize screen
        screen_gray = toGray(screen)

        # thresholding - otsu seems to be doing better
        blur = cv2.GaussianBlur(screen_gray,(5,1),0)
        ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
        if debug == 'on':
            cv2.imshow("screen adaptive", adapt_thresh)
            cv2.imshow("screen otsu", otsu_thresh)
        # compressed = extract_digits.compress(adapt_thresh,3)
        # cv2.imshow("compressed", compressed)
        kernel = np.ones((5,5),np.uint8)
        dilated = cv2.dilate(adapt_thresh,kernel,iterations=1)
        if debug == 'on':
            cv2.imshow("dilated", dilated)

        # bradley threshold
        pil_im = Image.fromarray(blur)
        bradley_thresh = faster_bradley_threshold(pil_im, 95, 10)
        open_cv_image = np.array(bradley_thresh)
        bradley_thresh = cv2.bitwise_not(open_cv_image)
        if debug == 'on':
            cv2.imshow("bradley", bradley_thresh)

        # digits appear in roughly the same place so...
        h,w = screen.shape[:2]
        # width = 21   
        # spacing = 5
        # slant = 15
        # y_offset = 10

        with open('C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/segvision.json') as json_data:
            params = json.load(json_data)

        width = params['digit_width']
        spacing = params['digit_spacing']
        y_offset_top = params['y_offset_top']
        y_offset_bottom = params['y_offset_bottom']
        digit_start = params['digit_start']
        digit_size = width*(h-y_offset_top-y_offset_bottom)
        cropped_digits = []
        for x in range(digit_start,w,width+spacing):
            roi = bradley_thresh[0+y_offset_top:h-y_offset_bottom, x:x+width]
            nonzero = np.count_nonzero(roi)
            # is a digit
            if float(nonzero/digit_size) >= .15:
                cv2.rectangle(screen, (x, 0+y_offset_top), (x+width, h-y_offset_bottom), (255,0,0), 2)
                cropped_digits.append(roi)

                # save digits
                name = "digit"+str(datetime.now())[20:]+".jpg"
                # print('saving', name)
                # cv2.imwrite(name, roi)
                if debug == 'on':
                    cv2.imshow("digit"+str(x), roi)
        if debug == 'on':
            cv2.imshow("screen",screen)

        # identify image
        identified = knn(cropped_digits,7)
        # print(identified)

        # cap.release()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return identified

    except TypeError:
        # cap.release()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # print('failed')
        return -1

    # cap.release()
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

def read_scale(debug='off'):
    cap = cv2.VideoCapture(2)
    ratio = 0.5
    # take snapshot
    ret, frame = cap.read()

    # rotate
    # frame = imutils.rotate(frame, 180)
    if debug == 'on':
        cv2.imshow('frame',frame)


    # img processing
    # img = cv2.imread("screen.png")
    img = frame
    cap.release()
    cv2.destroyAllWindows()
    return scale_to_digit(img)