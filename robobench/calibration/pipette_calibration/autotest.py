from snapshot import scale_to_digit, isolate_screen
import snapshot
import glob, os
import json
import cv2 
import numpy as np
from PIL import Image
from bradley_thresh import faster_bradley_threshold

def list_to_str(vals):
    res = ''
    for val in vals:
        res = res + str(val)
    return res

# checks if a screen was extracted form the scale img
# verification
def check_screen_extraction(dir):
    # load screens
    os.chdir(dir)

    # iterate through images
    num_imgs = 0
    failed = 0
    success = 0
    for file in glob.glob("*.jpg"):
        print('opening ' + file)
        screen = cv2.imread(file)

        # test screen extraction
        res = extracted_screen = snapshot.extract_screen(screen, file)
        if res == 0:
            success = success + 1

        num_imgs = num_imgs+1

    # results 
    print("num imgs:", str(num_imgs))
    print("screen detected", str(success/num_imgs*100), '%')

# finds the average aspect ratio of all the screens
def get_screen_info(dir):
    os.chdir(dir)

    total_h = 0
    total_w = 0
    count = 0
    for file in glob.glob('*.jpg'):
        print('opening'+file)
        crop = cv2.imread(file)

        # get screen dimensions
        h, w = crop.shape[:2]
        total_h = total_h + h
        total_w = total_w + w
        # print(w, h)

        count = count + 1

    return total_w//count, total_h//count

# rezies all of the screens into the same aspect ratio
def normalize_screens(dir, aspect_ratio):
    os.chdir(dir)
    for file in glob.glob('*.jpg'):
        img = cv2.imread(file)

        # resize image
        resize_w = 100
        resize_h = int(resize_w * float(1/aspect_ratio))

        resized = cv2.resize(img, (resize_w, resize_h), interpolation = cv2.INTER_AREA)
        # cv2.imshow("resized", resized)
        hsv_img = cv2.cvtColor(resized,cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_img)
        s.fill(255)
        v.fill(255)
        cv2.imshow('hsv', hsv_img[:,:,0])
        cv2.imshow('h', h)
        cv2.imshow('s', s)
        cv2.imshow('v', v)
        thresh, binarized = cv2.threshold(hsv_img[:,:,0], 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        cv2.imshow('OTSU', binarized)

        pil_im = Image.fromarray(hsv_img[:,:,0])
        bradley_thresh = faster_bradley_threshold(pil_im, 95, 10)
        open_cv_image = np.array(bradley_thresh)
        bradley_thresh = cv2.bitwise_not(open_cv_image)

        cv2.imshow('bradleuy', bradley_thresh)

        # # to grayscale
        # gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
        # equ = cv2.equalizeHist(gray.copy())

        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        # gray = clahe.apply(gray)
        
        # cv2.imshow('gray', gray)
        # cv2.imshow('his', equ)

        # # binarize img
        # # bradley threshold
        # pil_im = Image.fromarray(gray)
        # bradley_thresh = faster_bradley_threshold(pil_im, 95, 10)
        # open_cv_image = np.array(bradley_thresh)
        # bradley_thresh = cv2.bitwise_not(open_cv_image)

        # cv2.imshow('bradleuy', bradley_thresh)
        cv2.waitKey(0)

        # write to new folder
        cv2.imwrite(r"C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms/"+file, resized)

if __name__ == '__main__':
    img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/screen" 
    screen_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/crops"
    normed_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms"
    # load img digit key from json file
    os.chdir(img_dir)
    with open('key.json') as json_data:
        key = json.load(json_data)

    # check_screen_extraction(img_dir)
    w, h = get_screen_info(screen_dir)
    aspect = float(w/h)
    # print(aspect)

    normalize_screens(screen_dir, aspect)

    # go through all the normed screens and binarize them





