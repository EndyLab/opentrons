import numpy as np
import cv2
from imutils import perspective
from imutils import contours
from skimage import exposure

DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 1, 0): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1): 5,
    (1, 1, 0, 1, 1, 1, 1): 6,
    (1, 0, 1, 0, 0, 1, 0): 7,
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
    box = np.int0(box)
    img2 = img.copy()
    cv2.drawContours(img2,[box],0,(0,0,255),2)
    return img2


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
    cv2.imshow("bounding rect", draw_rect(img, screenContour))
    return pts


ratio = 0.2
img = cv2.imread("test.jpg")
img_scaled = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)

# crop the screen
pts = find_screen(img_scaled)
print("poinrt",pts)

# transform image so it is easier to parse
warped = perspective.four_point_transform(img_scaled, pts)
warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
warped_gray = exposure.rescale_intensity(warped_gray, out_range = (0, 255))
cv2.imshow("transform", warped_gray)
cv2.imshow("gray", warped)

# blur might not be necessary
blur = warped_gray
# blur = cv2.GaussianBlur(warped_gray,(3,3),0)
# cv2.imshow("grayblur", blur)

# make into binary image
ret,thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
# thresh = cv2.morphologyEx(warped_thresh, cv2.MORPH_OPEN, kernel)
cv2.imshow("cleaned up", thresh)


# dilate to join together segments
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1,5))
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
dilation = cv2.dilate(thresh,kernel,iterations = 1)
cv2.imshow("dilated", dilation)

# get contours of individual digits
img2, cnts, hier = cv2.findContours(dilation.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

# print(len(cnts))
# hull = cv2.convexHull(cnts[5])
# cv2.imshow("bounding rect digits", draw_rect(warped, hull))

# get digits
digits = []
for c in cnts:
    """ hull vs rect?
    hull = cv2.convexHull(c)
    temp = draw_rect(temp, hull)
    """
    (x, y, w, h) = cv2.boundingRect(c)
    rect_coords = (x,y,w,h)
    print("coords",rect_coords)

    # if the contour is sufficiently large, it must be a digit
    if (w >= 15 or w >= 0 and w <=10) and (h >= 40 and h <= 50):
        #""" optional - drawing the bounding box is for visual clarity
        # compute the bounding box of the contour

        # the digit 1
        if (w <= 10):
            rect_coords = (x-12,y-3,w+12,h+2)
            res = cv2.rectangle(warped,(x-10,y),(x+w,y+h),(0,255,0),2)
        else:
            res = cv2.rectangle(warped,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow("RECT TEST", res)
        print("coords that passed",(x, y, w, h))
        #"""

        # add digit coords to lsit
        # digits.append(c)
        digits.append(rect_coords)

# loop over digit contours
num=0
identified = []
used_pic = dilation.copy()
cv2.imshow("DILATION WTF", dilation)

# the result image with the identified numbers
res = img_scaled.copy()

for c in digits:
    # extract the digit from the screen picture
    # (x, y, w, h) = cv2.boundingRect(c)
    x = c[0]
    y = c[1]
    w = c[2]
    h = c[3]
    roi = used_pic[y:y + h, x:x + w]
    title = "cropped"+str(num)
    cv2.imshow(title, roi)

    # compute the width and height of each of the 7 segments
    # we are going to examine
    (roiH, roiW) = roi.shape
    (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
    dHC = int(roiH * 0.05)

    # define the set of 7 segments
    segments = [
        ((0, 0), (w, dH)),  # top
        ((0, 0), (dW, h // 2)), # top-left
        ((w - dW, 0), (w, h // 2)), # top-right
        ((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
        ((0, h // 2), (dW, h)), # bottom-left
        ((w - dW, h // 2), (w, h)), # bottom-right
        ((0, h - dH), (w, h))   # bottom
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

        print("totla:", total, "area:",area)
 
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
    print("POINTS:", pts)
    top_left = pts[0]
    bot_left = pts[1]
    top_right = pts[2]
    bot_right = pts[3]

    x_temp = x+top_left[0]
    y_temp = y+top_left[1]
    start_coords = (x_temp,y_temp)
    end_coords = (x_temp+w, y_temp+h)

    cv2.rectangle(res, start_coords, end_coords, (0, 255, 0), 1)
    cv2.putText(res, str(number), (x_temp, y_temp - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

    cv2.rectangle(warped, (x,y), (x+w,y+h), (0, 255, 0), 1)
    cv2.putText(warped, str(number), (x - 30, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

    num=num+1

cv2.imshow("result", res)
cv2.imshow("display", warped)
cv2.waitKey(0)
cv2.destroyAllWindows()