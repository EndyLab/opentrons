import numpy as np
import cv2
from imutils import perspective
from imutils import contours
from skimage import exposure
from skimage.filters import threshold_otsu, threshold_local
from matplotlib import pyplot as plt
import glob, os

DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 1, 0): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1): 5,
    (1, 1, 0, 1, 1, 1, 1): 6,
    (1, 1, 1, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9
}

def get_points(contourPoints):
    x = []
    y = []
    for point in contourPoints:
        coord = point[0]
        x.append(coord[0])
        y.append(coord[1])
        # print(coord)

    # print("x:", x,"y:",y)
    pts = np.array([(x[0], y[0]), (x[1], y[1]), (x[2], y[2]), (x[3], y[3])])
    # print(pts)
    return pts

def draw_rect(img, contour):
    # bounding rectangle
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    # print("box points!!!:", box)
    box = np.int0(box)
    img2 = img.copy()
    cv2.drawContours(img2,[box],0,(0,0,255),2)
    return img2, box

def find_screen(img):
    # turn img gray
    img2 = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray", img2)

    # threshold
    # ret, thresh = cv2.threshold(img2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # get contours
    # img2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # edges
    # egde works better
    edges = cv2.Canny(img,100,200)
    cv2.imshow("edge", edges)
    img2, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # sort contours
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]

    # loop over contours
    screenContour = None
    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
     
        # if our approximated contour has four points, then we can assume that we have found our screen
        if len(approx) == 4:
            screenContour = approx
            cv2.drawContours(img,screenContour,-1,(0,255,0),3)
            break

    pts = get_points(screenContour)

    # bounding rectangle
    temp, box =  draw_rect(img, screenContour)
    cv2.imshow("bounding rect", temp)
    return pts

def binarize_img(img):
    # make it gray in order to prepare it for threshold command
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = exposure.rescale_intensity(img_gray, out_range = (0, 255))
    # cv2.imshow("transform gray", img_gray)
    # cv2.imshow("img", img)

    # cv2.imshow("binary adaptive", binary_adaptive)

    # blur might not be necessary
    # blur = img_gray
    # blur = cv2.GaussianBlur(img_gray,(3,3),0)
    # cv2.imshow("grayblur", blur)

    # make into binary image
    ret,otsu_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    adapt_thresh = cv2.adaptiveThreshold(img_gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    opening = cv2.morphologyEx(adapt_thresh, cv2.MORPH_OPEN, kernel)
    # cv2.imshow("cleaned up", adapt_thresh)
    # cv2.imshow("cleaned up pt 2", opening)

    # dilate to join together segments
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT,(1,5))
    # kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    otsu_dilated = cv2.dilate(otsu_thresh,kernel2,iterations = 1)
    # cv2.imshow("dilated", otsu_dilated)

    adapt_dilated = cv2.dilate(opening,kernel2,iterations = 1)
    # cv2.imshow("dilated222", adapt_dilated)

    titles = ['gray', 'adaptive thresholding','otsu thresh','opened adaptive img', 'dilated otsu', 'dilated adaptive']
    images = [img_gray, adapt_thresh, otsu_thresh, opening, otsu_dilated, adapt_dilated]

    """
    for i in range(0,len(titles)):
        plt.subplot(3,3,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()

    """
    return otsu_dilated


def find_digits(img):
    # get contours of individual digitCoords
    img2, cnts, hier = cv2.findContours(img.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    # get digitCoords
    # res = img.copy
    res = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    digitCoords = []
    for c in cnts:
        # ll vs rect?
        # hull = cv2.convexHull(c)
        # temp = draw_rect(temp, hull)
        (x, y, w, h) = cv2.boundingRect(c)
        rect_coords = (x,y,w,h)
        # print("coords",rect_coords)

        # if the contour is sufficiently large, it must be a digit
        if (w >= 15 or w >= 0 and w <=10) and (h >= 40 and h <= 50):
            #""" optional - drawing the bounding box is for visual clarity
            # compute the bounding box of the contour

            # the digit 1
            if (w <= 10):
                rect_coords = (x-12,y-3,w+12,h+2)
                cv2.rectangle(res,(x-12,y-3),(x+w,y+h-1),(0,255,0),2)
            else:
                cv2.rectangle(res,(x,y),(x+w,y+h),(0,255,0),2)
            
            # print("coords that passed",(x, y, w, h))
            #"""

            # add digit coords to lsit
            # digitCoords.append(c)
            digitCoords.append(rect_coords)

    cv2.imshow("RECT TEST", res)
    return digitCoords

def identify_digits(img, digitCoords):
    num=0
    identified = []
    for c in digitCoords:
        # extract the digit from the screen picture
        x = c[0]
        y = c[1]
        w = c[2]
        h = c[3]
        roi = img[y:y + h, x:x + w]
        title = "cropped"+str(num)
        cv2.imshow(title, roi)

        # compute the width and height of each of the 7 segments we are going to examine
        (roiH, roiW) = roi.shape
        (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
        dHC = int(roiH * 0.05)

        # define the set of 7 segments
        segments = [
            ((dW, 0), (w-dW, dH)),  # top
            ((0, 0), (dW, h // 2)), # top-left
            ((w - dW, 0), (w, h // 2)), # top-right
            ((dW, (h // 2) - dHC) , (w-dW, (h // 2) + dHC)), # center
            ((0, h // 2), (dW, h)), # bottom-left
            ((w - dW, h // 2), (w, h)), # bottom-right
            ((dW, h - dH), (w-dW, h))   # bottom
        ]

        on = [0] * len(segments)
        # loop over the segments
        for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
            # extract the segment ROI, count the total number of
            # thresholded pixels in the segment, and then compute
            # the area of the segment
            seg = roi[yA:yB, xA:xB]
            title="segment rip" + str(i)
            cv2.imshow(title, roi[yA:yB, xA:xB])

            # number of black pixels
            total = cv2.countNonZero(seg)
            area = (xB - xA) * (yB - yA)

            # print("totla:", total, "area:",area)
     
            # if the total number of non-zero pixels is greater than
            # 50% of the area, mark the segment as "on"
            if total / float(area) > 0.4:
                on[i]= 1
     
        # lookup the digit and draw it on the image
        print("tuple",tuple(on))
        number = 0
        try:
            number = DIGITS_LOOKUP[tuple(on)]
        except KeyError:
            number = -1
        identified.append(number)

        num=num+1
    return identified

def find_top_left_point(rect_coords):
    # put everything in a list
    ordered = []
    for p in rect_coords:
        ordered.append(tuple(p))

    # print("ordered:", ordered)

    # sort ascending x
    ordered.sort(key=lambda tup: tup[0])
    # print("after sort:", ordered)
    ordered = ordered[:2]

    # sort descending y
    ordered.sort(key=lambda tup: tup[1])
    # print("after sort:", ordered[0])

    return ordered[0]
            

def display_digits(orig_img, screenCoords, digitCoords, identified):
    top_left = find_top_left_point(screenCoords)

    for j, c in enumerate(digitCoords):
        x = c[0]
        y = c[1]
        w = c[2]
        h = c[3]

        x_temp = x+top_left[0]
        y_temp = y+top_left[1]
        start_coords = (x_temp,y_temp)
        end_coords = (x_temp+w, y_temp+h)

        cv2.rectangle(orig_img, start_coords, end_coords, (0, 255, 0), 1)
        cv2.putText(orig_img, str(identified[j]), (x_temp, y_temp - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

        # cv2.rectangle(warped, (x,y), (x+w,y+h), (0, 255, 0), 1)
        # cv2.putText(warped, str(identified[j]), (x - 30, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

def process_digits_img(img):
    # ratio = 0.2
    # img = cv2.imread("test.jpg")
    # img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)

    # crop the screen
    screen_pts = find_screen(img)
    # print("poinrt",screen_pts)

    # transform image so it is easier to parse
    warped = perspective.four_point_transform(img, screen_pts)
    processed_screen = binarize_img(warped)

    digitCoords = find_digits(processed_screen)

    # the result image with the identified numbers
    output_img = img.copy()

    identifiedDigits = identify_digits(processed_screen, digitCoords)
    # print("answer:", identifiedDigits)

    display_digits(output_img, screen_pts, digitCoords, identifiedDigits)
    cv2.imshow("THERE IT IS", output_img)
    cv2.imshow("display", warped)

    return identifiedDigits, output_img, screen_pts, processed_screen

# main function
ratio = 0.2

test_images = []
res_images = []
bin_images = []
screen_pts = []
solution = [(0,5,1,1)]

# load test files
img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/test_imgs" 
if os.path.exists(img_dir):
    os.chdir(img_dir)
    for file in glob.glob("*.jpg"):
        print(file)
        test_images.append(img_dir+'/'+str(file))

for j in range(0,len(test_images)):
    img = cv2.imread(test_images[j])
    img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
    numbers, res, pts, binary_img = process_digits_img(img_scaled)
    print("RESULT:",numbers)
    res_images.append(res)
    bin_images.append(binary_img)
    screen_pts.append(find_top_left_point(pts))

for i in range(0,len(test_images)):
    pt = screen_pts[i]
    x = pt[0]
    y = pt[1]
    w = 200
    h = 100
    crop_img = res_images[i][y-50:y+h, x-50:x+w] 
    plt.subplot(3,3,i+1),plt.imshow(crop_img)
    plt.title(test_images[i])
    plt.xticks([]),plt.yticks([])
plt.show()

for i in range(0,len(test_images)):
    pt = screen_pts[i]
    x = pt[0]
    y = pt[1]
    w = 200
    h = 100
    plt.subplot(3,3,i+1),plt.imshow(bin_images[i])
    plt.title("binary img"+str(i))
    plt.xticks([]),plt.yticks([])
plt.show()

cv2.waitKey(0)
cv2.destroyAllWindows()