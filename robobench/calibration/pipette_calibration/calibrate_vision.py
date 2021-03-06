import cv2
import numpy as np
from skimage import exposure
from imutils import contours
from imutils import perspective
import imutils
# import extract_digits
import glob, os
from PIL import Image
from bradley_thresh import faster_bradley_threshold
from classify import knn
import json

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
    cv2.imshow("gray",img_gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img_gray)
    cv2.imshow("gray optimzed",cl1)
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

def getScreen(img):
    cv2.imshow("passed img", img)
    bin_img = img.copy()
    img3, contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    # cv2.drawContours(img,contours,-1,(0,255,0),3)
    windowH, windowW = img.shape
    window_area = windowW*windowH
    screenContour = None
    found = 0
    for contour in contours:
        if found == 1:
            break
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.01 * peri, True)

        # print(approx)
       
     
        # if our approximated contour has four points, then we can assume that we have found our screen
        area = cv2.contourArea(approx)
        if len(approx) == 4 and area >= .10 * window_area and area <= .50 * window_area:
            tl = find_top_left_point(approx)
            # print(tl)
            color = cv2.cvtColor(img.copy(),cv2.COLOR_GRAY2RGB)
            cv2.circle(color,(tl[0],tl[1]), 1, (0,0,255), -1)
            cv2.imshow("circle", color)
            # print("color:", bin_img[tl[1]+1][tl[0]+1])
            if bin_img[tl[1]+1][tl[0]+1] != 255:
                screenContour = approx
                found = 1
                break

    return screenContour

cap = cv2.VideoCapture(2)
ratio = 0.5
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # rotate
    frame = imutils.rotate(frame, 180)
    cv2.imshow('frame',frame)
    cv2.moveWindow('frame',0,0)

    # img processing
    # img = cv2.imread("screen.png")
    img = frame
    img = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)

    # turn img gray
    img_gray = toGray(img)

    # adaptive threshold
    blur = cv2.GaussianBlur(img_gray,(5,5),0)
    ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    cv2.imshow("adaptive threshold", adapt_thresh)
    cv2.imshow("otsu threshold", otsu_thresh)

    # get screen
    screenContour = getScreen(adapt_thresh)
    pts = get_points(screenContour)

    # get digits
    try:
        len(pts)
        box = img.copy()
        rect_pts = draw_rect(box, screenContour)
        screen = perspective.four_point_transform(img, rect_pts)

        cv2.imshow("detected screen", box)
        
        # binarize screen
        screen_gray = toGray(screen)

        # thresholding - otsu seems to be doing better
        blur = cv2.GaussianBlur(screen_gray,(5,1),0)
        ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
        cv2.imshow("screen adaptive", adapt_thresh)
        cv2.imshow("screen otsu", otsu_thresh)
        # compressed = extract_digits.compress(adapt_thresh,3)
        # cv2.imshow("compressed", compressed)
        kernel = np.ones((5,5),np.uint8)
        dilated = cv2.dilate(adapt_thresh,kernel,iterations=1)
        cv2.imshow("dilated", dilated)

        # bradley threshold
        pil_im = Image.fromarray(blur)
        bradley_thresh = faster_bradley_threshold(pil_im, 95, 10)
        open_cv_image = np.array(bradley_thresh)
        bradley_thresh = cv2.bitwise_not(open_cv_image)
        cv2.imshow("bradley", bradley_thresh)

        # finding contours of bradley threshold
        # img3, contours, hierarchy = cv2.findContours(bradley_thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        # contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
        # cv2.drawContours(screen,contours,-1,(0,255,0),1)
        # cv2.imshow("contours", screen)

        # digits appear in roughly the same place so...
        h,w = screen.shape[:2]
        def nothing(x):
            pass
        # slidebars and window for calibration
        cv2.namedWindow('digits')
        cv2.moveWindow('digits',650,0)
        cv2.createTrackbar('width', 'digits', 0, 100, nothing)
        cv2.createTrackbar('spacing', 'digits', 0, 50, nothing)
        cv2.createTrackbar('y_offset_top', 'digits', 0, 50, nothing)
        cv2.createTrackbar('y_offset_bottom', 'digits', 0, 50, nothing)
        cv2.createTrackbar('digit_start', 'digits', 0, 100, nothing)

        with open('segvision.json') as json_data:
            params = json.load(json_data)

        width = params['digit_width']
        spacing = params['digit_spacing']
        y_offset_top = params['y_offset_top']
        y_offset_bottom = params['y_offset_bottom']
        digit_start = params['digit_start']

        # e: edit params
        crop = False
        if cv2.waitKey(1) & 0xFF == ord('e'):
            while True:
                # get params
                # cv2.setTrackbarPos('width', 'digits', width)
                # cv2.setTrackbarPos('spacing', 'digits', spacing)
                # cv2.setTrackbarPos('y_offset_top', 'digits', y_offset_top)
                # cv2.setTrackbarPos('y_offset_bottom', 'digits', y_offset_bottom)
                # cv2.setTrackbarPos('digit_start', 'digits', digit_start)

                # c: crop digits
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    crop = True

                digit_size = width*(h-y_offset_top-y_offset_bottom)
                # show images
                cropped_digits = []
                temp = screen.copy()
                for x in range(digit_start,w,width+spacing):
                    roi = bradley_thresh[0+y_offset_top:h-y_offset_bottom, x:x+width]
                    nonzero = np.count_nonzero(roi)
                    # is a digit
                    if float(nonzero/digit_size) >= .15:
                        
                        cv2.rectangle(temp, (x, 0+y_offset_top), (x+width, h-y_offset_bottom), (255,0,0), 2)
                        if crop == True:
                            cropped_digits.append(roi)
                            cv2.imshow("digit"+str(x), roi)

                cv2.imshow('digits',temp)

                if cv2.getTrackbarPos('width', 'digits') > 0:
                    width = cv2.getTrackbarPos('width', 'digits') 
                if cv2.getTrackbarPos('spacing', 'digits') > 0:
                    spacing = cv2.getTrackbarPos('spacing', 'digits')
                if cv2.getTrackbarPos('y_offset_top', 'digits') > 0:
                    y_offset_top = cv2.getTrackbarPos('y_offset_top', 'digits')
                if cv2.getTrackbarPos('y_offset_bottom', 'digits') > 0:
                    y_offset_bottom = cv2.getTrackbarPos('y_offset_bottom', 'digits')
                if cv2.getTrackbarPos('digit_start', 'digits') > 0:
                    digit_start = cv2.getTrackbarPos('digit_start', 'digits')

                # w: write params to json
                if cv2.waitKey(1) & 0xFF == ord('w'):
                    data =  {
                                'digit_spacing': spacing,
                                'digit_start': digit_start,
                                'digit_width': width,
                                'y_offset_bottom': y_offset_bottom,
                                'y_offset_top': y_offset_top
                            }
                    print(data)
                    with open('segvision.json', 'w+') as f:
                        json.dump(data, f,sort_keys=True, indent=4)

                # i: identify image on command
                if cv2.waitKey(1) & 0xFF == ord('i'):
                    identified = knn(cropped_digits,7)
                    print(identified)

                # s: save images
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    for i, digit in enumerate(cropped_digits):
                        cv2.imwrite("digit"+str(i)+".jpg", roi)

                # esc: quit
                if cv2.waitKey(1) & 0xFF == 27: 
                    break

                crop = False


    except TypeError:
        pass

    # quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
