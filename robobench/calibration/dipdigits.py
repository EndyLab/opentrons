import numpy as np
import cv2
from imutils import perspective
from imutils import contours
import imutils
from skimage import exposure
from skimage.filters import threshold_otsu, threshold_local
from matplotlib import pyplot as plt
import glob, os
from bradley_thresh import faster_bradley_threshold

import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
from PIL import Image

DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 0, 1): 2,
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
    img2 = img.copy()
    cv2.drawContours(img2,[box],0,(0,0,255),2)
    return img2, box

def within(val, target, error):
    return abs(val-target) < error

def find_screen(img, debug='off'):
    # turn img gray
    img2 = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    if debug=='on':
        cv2.imshow("gray", img2)

    # img processing
    blur = cv2.GaussianBlur(img2,(5,5),0)

    ret,otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    if debug=='on':
        cv2.imshow("otsu", otsu_thresh)
    adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    kernel = np.ones((1,3),np.uint8)
    opening = cv2.morphologyEx(otsu_thresh, cv2.MORPH_OPEN, kernel)
    cv2.imshow("adaptive thresh - opening", opening)
    
    # get contours
    img3, contours, hierarchy = cv2.findContours(otsu_thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img3, contours1, hierarchy = cv2.findContours(adapt_thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img3, contours2, hierarchy = cv2.findContours(opening,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = contours1
    """
    # bradley thresh
    blur2 = cv2.GaussianBlur(img2,(5,3),0)
    pil_im = Image.fromarray(blur2)
    pil_im.show()
    bradley_thresh = faster_bradley_threshold(pil_im, 60)
    open_cv_image = np.array(bradley_thresh) 
    cv2.imshow("bradley", open_cv_image)
    bradley_thresh.show()
    """
    # egde works better?? 
    # edges = cv2.Canny(img,100,200)
    # cv2.imshow("edge", edges)
    # img2, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # sort contours
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]

    lcd_cascade = cv2.CascadeClassifier('lcd_screen_detector.xml')

    # faces = lcd_cascade.detectMultiScale(img2, 1.3, 5)
    # for (x,y,w,h) in faces:
    #     cv2.rectangle(img2,(x,y),(x+w,y+h),(255,0,0),2)
    #     roi_gray = img2[y:y+h, x:x+w]
    # cv2.imshow('img',img2)

    # loop over contours
    screenContour = None
    windowH, windowW = img2.shape
    window_area = windowW*windowH
    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
     
        # if our approximated contour has four points, then we can assume that we have found our screen
        area = cv2.contourArea(approx)
        print("len:", len(approx), "loop area:", area)
        if len(approx) == 4 and area < window_area//4:
            screenContour = approx
            cv2.drawContours(img,screenContour,-1,(0,255,0),3)
            area = cv2.contourArea(screenContour)
            print("area:", area, "window:", window_area)
            break

    area = cv2.contourArea(screenContour)
    print("area:", area)
    pts = get_points(screenContour)

    temp, box = draw_rect(img, screenContour)
    if debug=='on':
        cv2.imshow("adaptive thresh", adapt_thresh)
        cv2.imshow("bounding rect", temp)
    return pts

def crop_screen(img, pts):
    return perspective.four_point_transform(img, pts)

def binarize_img(img):
    # make it gray in order to prepare it for threshold command
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = exposure.rescale_intensity(img_gray, out_range = (0, 255))
    # cv2.imshow("transform gray", img_gray)
    # cv2.imshow("img", img)

    # cv2.imshow("binary adaptive", binary_adaptive)

    # blur might not be necessary
    blur = img_gray
    blur = cv2.GaussianBlur(img_gray,(3,3),0)
    cv2.imshow("grayblur", blur)

    # make into binary image
    ret,otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    adapt_thresh = cv2.adaptiveThreshold(img_gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    opening = cv2.morphologyEx(adapt_thresh, cv2.MORPH_OPEN, kernel)
    # cv2.imshow("cleaned up", adapt_thresh)
    # cv2.imshow("cleaned up pt 2", opening)

    # dilate to join together segments
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT,(3,5))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    # kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    otsu_dilated = cv2.dilate(otsu_thresh,kernel1,iterations = 1)
    adapt_dilated = cv2.dilate(opening,kernel1,iterations = 1)
    # cv2.imshow("dilated222", adapt_dilated)
    
    # erode
    otsu_eroded= cv2.erode(otsu_dilated,kernel2,iterations = 1)
    adapt_eroded = cv2.erode(adapt_dilated,kernel2,iterations = 1)

    # dilate/erode again
    otsu_dilated = cv2.dilate(otsu_eroded,kernel1,iterations = 1)
    adapt_dilated = cv2.dilate(adapt_eroded,kernel1,iterations = 1)
    # cv2.imshow("dilated222", adapt_dilated)

    # erode
    otsu_eroded= cv2.erode(otsu_dilated,kernel2,iterations = 1)
    adapt_eroded = cv2.erode(adapt_dilated,kernel2,iterations = 1)

    
    titles = ['gray', 'adaptive thresholding','otsu thresh','opened adaptive img', 'dilated otsu', 'dilated adaptive']
    images = [img_gray, adapt_thresh, otsu_thresh, opening, otsu_dilated, adapt_dilated]

    """
    for i in range(0,len(titles)):
        plt.subplot(3,3,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()

    """
    return adapt_eroded


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
    if len(screen_pts) == 0:
        return

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

    raw_screen = warped
    return identifiedDigits, output_img, screen_pts, raw_screen, processed_screen

def digit_match(img, templates):
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = img
    cv2.imshow('res.pnsdsdsdg',img_gray)

    height, width = img.shape 
    print("IMG y:",height,"x:",width)

    # print("TEMPLATES", templates)
    for img_file in templates:
        # loop over the scales of the image
        template = cv2.imread(img_file,0)
        cv2.imshow('template',template)
        t_height, t_width = template.shape 
        print("TEMPLATE y:",t_height,"x:",t_width)
        found = (0,0,0)
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(template, width = int(template.shape[1] * scale))
            r = template.shape[1] / float(resized.shape[1])
     
            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < height or resized.shape[1] < width:
                break
            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            result = cv2.matchTemplate(img_gray, resized, TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # if we have found a new maximum correlation value, then ipdate
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)
 
        # unpack the bookkeeping varaible and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
     
        # draw a bounding box around the detected result and display the image
        cv2.rectangle(img_gray, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.imshow("Image", img_gray)

        # template = cv2.Canny(template, 50, 200)

        # (tH, tW) = template.shape[:2]
        # cv2.imshow("Template", template)

        # w, h = template.shape[::-1]

        # res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        # threshold = 0.8
        # loc = np.where( res >= threshold)

        # for pt in zip(*loc[::-1]):
        #     cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
        #     cv2.imshow('Detected',img)

    cv2.imshow('res.png',img_gray)

# return binarized images
def binarize_entire_dir(img_dir):
    test_images = []
    if os.path.exists(img_dir):
        os.chdir(img_dir)
        for file in glob.glob("*.jpg"):
            img = cv2.imread(file)
            test_images.append(img)
            # test_images.append(img_dir+'/'+str(file))

        ratio = 0.2
        bin_images = []
        # test_images = test_images[:2]
        for img in test_images:
            # img = cv2.imread(test_images[j])
            img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
            # crop the screen
            screen_pts = find_screen(img_scaled)
            # transform image so it is easier to parse
            warped = perspective.four_point_transform(img_scaled, screen_pts)
            processed_screen = binarize_img(warped)
            bin_images.append(processed_screen)

    return bin_images


def binarize_img_dir(img_dir):
    test_images = []
    if os.path.exists(img_dir):
        os.chdir(img_dir)
        for file in glob.glob("*.jpg"):
            # test files
            if 'test' in file:
                test_images.append(img_dir+'/'+str(file))

        ratio = 0.2
        bin_images = []
        for j in range(0,len(test_images)):
            img = cv2.imread(test_images[j])
            img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
            # crop the screen
            screen_pts = find_screen(img_scaled)
            # transform image so it is easier to parse
            warped = perspective.four_point_transform(img_scaled, screen_pts)
            processed_screen = binarize_img(warped)
            bin_images.append(processed_screen)

    return bin_images


# main function
if __name__ == '__main__':
    ratio = 0.2

    test_images = []
    res_images = []
    screen_images = []
    bin_images = []
    screen_pts = []
    solution = [(0,5,1,1)]
    templates = []

    # load test files
    img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/test_imgs" 
    template_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/templates" 
    if os.path.exists(template_dir):
        print("yeasss")
        os.chdir(template_dir)
        for file in glob.glob("*.jpg"):
            # templates
            print(file)
            if 'template' in file:
                templates.append(template_dir+'/'+str(file))

    if os.path.exists(img_dir):
        os.chdir(img_dir)
        for file in glob.glob("*.jpg"):
            # test files
            if 'test' in file:
                test_images.append(img_dir+'/'+str(file))
            

    for j in range(0,len(test_images)):
        img = cv2.imread(test_images[j])
        img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
        numbers, res, pts, screen, binary_img = process_digits_img(img_scaled)
        print("RESULT:",numbers)
        res_images.append(res)
        screen_images.append(screen)
        bin_images.append(binary_img)
        screen_pts.append(find_top_left_point(pts))

    for i in range(0,len(test_images)):
        pt = screen_pts[i]
        x = pt[0]
        y = pt[1]
        w = 200
        h = 100

        plt.subplot(3,3,i+1),plt.imshow(bin_images[i])
        plt.title("binary img"+str(i))
        plt.xticks([]),plt.yticks([])

        # tesseract ocr
        name = "bin"+str(i)+".jpg"
        cv2.imwrite(name,bin_images[i])
        # print("OCR:",pytesseract.image_to_string(Image.open(name)))

    plt.show()

    # for i in range(0,len(test_images)):
    #     name = img_dir+"/bin"+str(i)+".jpg"
    #     bin_img = cv2.imread(name)
    #     img_gray = cv2.cvtColor(bin_img, cv2.COLOR_BGR2GRAY)
    #     cv2.imshow("display GRAY SDSD", img_gray)
    #     # template = cv2.imread(templates[0],0)
    #     # cv2.imshow('template',template)
    #     digit_match(img_gray, templates)

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



    cv2.waitKey(0)
    cv2.destroyAllWindows()