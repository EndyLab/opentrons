import numpy as np
import cv2
from imutils import perspective
from skimage import exposure

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
"""
img_gray = cv2.cvtColor(img_scaled,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(img_gray,64,255,0)
img2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

# loop over contours
contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
# largest contour is img box for test image remove for real camera
contours = contours[1:]
for contour in contours:
    # approximate the contour
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
 
    # if our approximated contour has four points, then we can assume that we have found our screen
    if len(approx) == 4:
        screenContour = approx
        # print(screenContour)
        cv2.drawContours(img_scaled,screenContour,-1,(0,255,0),3)
        cv2.imshow("screen", img_scaled)
        break

# perspective transform
print(type(screenContour))
# pts = np.array(screenContour)
pts = np.array([(110, 575), (305, 575), (310, 672), (102, 672)])
print(pts)
warped = perspective.four_point_transform(img_scaled, pts)
cv2.imshow("transform", warped)
"""

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
img2, cnts, hier = cv2.findContours(dilation,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
    print("coords",(x, y, w, h))

    # if the contour is sufficiently large, it must be a digit
    if (w >= 15 or w >= 0 and w <=10) and (h >= 40 and h <= 50):
        # compute the bounding box of the contour
        res = cv2.rectangle(warped,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow("RECT TEST", res)
        print("coords that passed",(x, y, w, h))

        # add digit coords to lsit
        digits.append(c)

# identify digits

cv2.waitKey(0)
cv2.destroyAllWindows()