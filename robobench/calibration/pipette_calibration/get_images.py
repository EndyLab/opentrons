import cv2
import imutils
import glob, os
from datetime import datetime

# takes picture automatically
# ----------------
# port: camera port
# angle: angle you want screen to be rotated
# directory: directoy where images will be saved
def take_pic(port, angle, directory):
    # take picture
    cap = cv2.VideoCapture(port)
    ret, frame = cap.read()

    # rotate
    frame = imutils.rotate(frame, angle)

    # save image
    date = str(datetime.now())
    name = "screen"+date[:10]+"_"+date[20:]+".jpg"
    print('saving', name)
    os.chdir(directory)
    cv2.imwrite(name, frame)

# takes pictures on key press
def livestream(port, angle, directory):
    cap = cv2.VideoCapture(port)
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # rotate
        frame = imutils.rotate(frame, angle)
        cv2.imshow('frame',frame)

        # on key press 's'
        if cv2.waitKey(1) & 0xFF == ord('s'):
            date = str(datetime.now())
            name = "screen"+date[:10]+'_'+date[20:]+".jpg"
            print('saving', name)
            os.chdir(directory)
            cv2.imwrite(name, frame)

        # exit on esc
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()
