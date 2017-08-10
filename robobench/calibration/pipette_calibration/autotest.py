from snapshot import scale_to_digit, isolate_screen
import snapshot
import glob, os
import json
import cv2 
import numpy as np
from PIL import Image
from bradley_thresh import faster_bradley_threshold
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline


from scipy import signal

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
        res = snapshot.extract_screen(screen, file)
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

def reduce_glare(img):
    # Converting image to LAB Color model
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    # cv2.imshow("lab",lab)

    # Splitting the LAB image to different channels 
    l, a, b = cv2.split(lab)
    # cv2.imshow('l_channel', l)
    # cv2.imshow('a_channel', a)
    # cv2.imshow('b_channel', b)

    # Applying CLAHE to L-channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    # cv2.imshow('CLAHE output', cl)

    # Merge the CLAHE enhanced L-channel with the a and b channel 
    limg = cv2.merge((cl,a,b))
    # cv2.imshow('limg', limg)

    # Converting image from LAB Color model to RGB model
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    # cv2.imshow('final', final)

    cv2.waitKey(0)
    return final

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

        # threshold using h channel of img
        reduced_glare = reduce_glare(resized)
        hsv_img = cv2.cvtColor(reduced_glare,cv2.COLOR_BGR2HSV)
        # cv2.imshow('glare less', hsv_img[:,:,0])

        # bradley thresholding for binarization
        pil_im = Image.fromarray(reduced_glare)
        bradley_thresh = faster_bradley_threshold(pil_im, 92, 20)
        open_cv_image = np.array(bradley_thresh)
        bradley_thresh = cv2.bitwise_not(open_cv_image)

        # cv2.imshow('bradley', bradley_thresh)
        # cv2.waitKey(0)

        # write to new folder
        cv2.imwrite(r"C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms/"+file, bradley_thresh)

# sliding window
BLACK = 255
WHITE = 0
def extract_digits(img):
    y_offset_top = 2
    y_offset_bottom = 3
    window_w = 13
    h, w = img.shape[:2]

    vals = []
    crop_start = []

    for x in range(w):
        if x + window_w > w:
            break
        roi = img[0+y_offset_top:h-y_offset_bottom, x:x+window_w]

        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_h, roi_w = roi.shape[:2]
        num_white = cv2.countNonZero(roi)
        num_pixels = roi_h*roi_w
        percent_white = float(num_white/num_pixels)
        print(percent_white)

        crop_start.append(x)
        vals.append(percent_white)

        # cv2.imshow('crop', roi)
        # cv2.waitKey(0)

    # plot graph of % white vs crop pos
    # plt.plot(crop_start, vals, 'ro')
    # plt.show()
    find_peaks(crop_start, vals)


def find_peaks(x, y):
    # curve fitting
    spl = UnivariateSpline(x,y,s=0,k=4)
    plt.plot(x,y,'ro',label = 'data')
    xs = np.linspace(x[0], x[-1], 1000)
    spl.set_smoothing_factor(0.001)
    plt.plot(xs,spl(xs), 'g', lw=3)

    # 1st derivative
    spl_d = spl.derivative(n=1)
    deriv = spl_d(xs)
    plt.plot(xs,deriv, 'y', lw=3)
    plt.show()

    # find peak indices
    peak_indices = signal.find_peaks_cwt(y, np.arange(1,10))
    print(peak_indices)


if __name__ == '__main__':
    img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/screen" 
    screen_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/crops"
    normed_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms"
    
    # # load img digit key from json file
    # os.chdir(img_dir)
    # with open('key.json') as json_data:
    #     key = json.load(json_data)
  
    # # check_screen_extraction(img_dir)
    # w, h = get_screen_info(screen_dir)
    # aspect = float(w/h)
    # # print(aspect)

    # normalize_screens(screen_dir, aspect)
    os.chdir(normed_dir)
    for file in glob.glob('*.jpg'):
        img = cv2.imread(file)
        # img = cv2.imread('screen2017-08-04_249038.jpg')
        cv2.imshow('orig', img)
        extract_digits(img)
        cv2.waitKey(0)






