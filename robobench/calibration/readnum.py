import cv2
import numpy as np
import dipdigits
from skimage import exposure
from imutils import contours
import extract_digits
import os
import label_image

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
        approx = cv2.approxPolyDP(contour, 0.005 * peri, True)
     
        # if our approximated contour has four points, then we can assume that we have found our screen
        area = cv2.contourArea(approx)
        
        if len(approx) == 4 and area >= .25 * window_area:
        	# print("len:", len(approx), "loop area:", area, "window:", window_area)
        	screenContour = approx
        	area = cv2.contourArea(screenContour)
        	break

    pts = dipdigits.get_points(screenContour)
 	# if screen is detected, display it
    try:
    	len(pts)
    	box = frame.copy()
    	rect_pts = draw_rect(box, screenContour)
    	screen = dipdigits.crop_screen(frame, rect_pts)

    	cv2.imshow("detected screen", box)
    	

    	# binarize screen
    	screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    	screen_gray = exposure.rescale_intensity(screen_gray, out_range = (0, 255))
    	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    	screen_clahe = clahe.apply(screen_gray)
    	cv2.imshow("gray screen",screen_clahe)

    	# thresholding - otsu seems to be doing better
    	blur = cv2.GaussianBlur(screen_clahe,(5,1),0)
    	ret, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    	adapt_thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
    	cv2.imshow("screen adaptive", adapt_thresh)
    	cv2.imshow("screen otsu", otsu_thresh)
    	# compressed = extract_digits.compress(adapt_thresh,4)
    	# cv2.imshow("compressed", compressed)
    	kernel = np.ones((5,5),np.uint8)
    	dilated = cv2.dilate(adapt_thresh,kernel,iterations=1)
    	cv2.imshow("dilated", dilated)

    	# finding contours of otsu
    	# img3, contours, hierarchy = cv2.findContours(otsu_thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    	# contours = sorted(contours, key = cv2.contourArea, reverse = True)[0:]
    	# print("BEGIINGIGN")
    	# print(len(contours))

    	# digits appear in roughly the same place so...
    	h,w = screen.shape[:2]
    	width = 60    	
    	spacing = 5
    	slant = 0
    	digit_size = width*(h-10-10)
    	digit_coords = []
    	for x in range(19,w,width+spacing):
    		roi = otsu_thresh[0+10:h-10,x-slant:x+width-slant]
    		nonzero = np.count_nonzero(roi)
    		# is a digit
    		if float(nonzero/digit_size) >= .10:
    			cv2.rectangle(screen, (x-slant, 0+10), (x+width-slant, h-10), (255,0,0), 2)
    			# digit = roi
    			digit_coords.append([(x-slant,0+10),(x+width-slant,h-10)])
    	cv2.imshow("screen",screen)

    	# identify image on command
    	if cv2.waitKey(1) & 0xFF == ord('i'):
    		reading = []
    		for coords in digit_coords:
    			x1 = coords[0][0]
    			y1 = coords[0][1]
    			x2 = coords[1][0]
    			y2 = coords[1][1]

    			digit = screen[y1:y2,x1:x2]
    			cv2.imwrite("digit.jpg",digit)
    			# digit = label_image.identify("digit.jpg")
    			# reading.append(digit)
    			cv2.putText(screen, "8", (x1, y1+100), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 5)
    			try:
    				os.remove("digit.jpg")
    			except:
    				pass
    		print("result:", reading)
    		cv2.imshow("screen digits",screen)

    except TypeError:
    	pass
    	continue
    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()