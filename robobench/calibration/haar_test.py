import numpy as np
import cv2

lcd_cascade = cv2.CascadeClassifier('lcd_screen_detector.xml')
img = cv2.imread('img (1).bmp')
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = img
faces = lcd_cascade.detectMultiScale(gray, 1.3, 5)
for (x,y,w,h) in faces:
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = img[y:y+h, x:x+w]
cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()