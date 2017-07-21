import cv2
import numpy as np
import dipdigits
from skimage import exposure
from imutils import contours

# 2 because 0 = webcam, 1 = backfacing cam, 2 = usb cam
cap = cv2.VideoCapture(2)
debug = 'on'

def draw_rect(img, contour):
    # bounding rectangle
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    # print("box points!!!:", box)
    box = np.int0(box)
    cv2.drawContours(img,[box],0,(0,0,255),4)
    return box


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # turn img gray
    img_gray = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2GRAY)
    img_gray = exposure.rescale_intensity(img_gray, out_range = (0, 255))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img_gray)
    cv2.imshow("gray",cl1)

    # adaptive threshold
    blur = cv2.GaussianBlur(cl1,(5,5),0)
    ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    cv2.imshow("adaptive threshold", adapt_thresh)
    cv2.imshow("otsu threshold", otsu_thresh)

    # get screen
    img3, contours, hierarchy = cv2.findContours(otsu_thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    # cv2.drawContours(frame,contours,-1,(0,255,0),3)
    windowH, windowW = img_gray.shape
    window_area = windowW*windowH
    screenContour = None
    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
     
        # if our approximated contour has four points, then we can assume that we have found our screen
        area = cv2.contourArea(approx)
        
        if len(approx) == 4 and area >= .25 * window_area:
        	print("len:", len(approx), "loop area:", area, "window:", window_area)
        	screenContour = approx
        	area = cv2.contourArea(screenContour)
        	break

    pts = dipdigits.get_points(screenContour)
    try:
    	len(pts)
    	box = draw_rect(frame, screenContour)
    except TypeError:
    	print("screen not found try again")
    # pts = dipdigits.find_screen(frame, debug)
    # tl_pt = dipdigits.find_top_left_point(pts)
    # print("points:",pts,"top left:",tl_pt)
    # screen = dipdigits.crop_screen(frame, pts)
    # h, w, channels = screen.shape
    # cv2.imshow("screen cropped", screen)
	# cv2.imwrite(name,screen)

    # edge detection
    # edges = cv2.Canny(frame,100,200)


    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()