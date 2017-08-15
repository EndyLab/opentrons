import glob, os
import json
import cv2 
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from datetime import datetime
from scipy import signal
import statistics

import screen_processing
from bradley_thresh import faster_bradley_threshold
from classify import knn

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

# optimize sliding window
# once you find the first digit, offset to find the next

WINDOW_MIN = 15
# use cliding window and graph to find 
def find_digit_start(img):
    y_offset_top = 2
    y_offset_bottom = 2
    h, w = img.shape[:2]

    master_crops = [] # x value of crop
    master_vals = [] # percent of white pixels
    master_widths = []

    for width in range(WINDOW_MIN, WINDOW_MIN+1, 1):
        # print('width:', width)
        crops = []
        vals = []
        for x in range(w):
            if x + width > w:
                break
            roi = img[0+y_offset_top:h-y_offset_bottom, x:x+width]
            # cv2.imshow('crop', roi)
            # cv2.waitKey(0)

            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi_h, roi_w = roi.shape[:2]
            num_white = cv2.countNonZero(roi)
            num_pixels = roi_h*roi_w
            percent_white = float(num_white/num_pixels)
            # print(percent_white)

            crops.append(x)


            vals.append(percent_white)

        master_crops.append(crops)
        master_vals.append(vals)
        master_widths.append(width)

    # find peaks for each window size
    for crop, val, width in zip(master_crops, master_vals, master_widths):
        peak = find_peaks(crop, val)
        # print('x coords:', peak)

        opt_vals = []
        # for peak in peaks:
        # crop at the peaks
        roi = img[0+y_offset_top:h-y_offset_bottom, peak:peak+width]
        temps = [cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)]
        # digit = knn(temps)
        # print(digit)
        opt_vals.append(val[peak])
        # print(val[peak])
        # cv2.imshow('crop', roi)
        # cv2.waitKey(0)
        # print(opt_vals, width)
    # print('digit start x coords:', peak)
    return peak

# crop digits
def crop_digits(img, y0, y1, x0, x1):
    # default set to fail
    ret = -1
    digit = img

    roi = img[y0:y1, x0:x1]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi_h, roi_w = roi.shape[:2]
    num_white = cv2.countNonZero(roi)
    num_pixels = roi_h*roi_w
    percent_white = float(num_white/num_pixels)

    if percent_white >= .35:
        ret = 0 # 0 = pass, -1 = fail
        digit = roi
        # cv2.imshow('digits', roi)
        # cv2.waitKey(0)

    return ret, digit, percent_white

class Digit(object):
    """ a Digit has an image, cropped image containing the digit, and coords o the crop
        Attributes:
            img = the screen with the digit
            crop_img = the cropped image of the digit
            coords = the coords of where the dogiot was cropped, a tuple of (x, y)
    """ 
    def __init__(self, screen, crop=None, coords=None):
        self.screen = screen
        self.crop = crop
        self.coords = coords

    def add_crop(self, img):
        self.crop = img

    def add_coords(self, coords):
        self.coords = coords

    def get_screen(self):
        return self.screen

    def get_crop(self):
        return self.crop

    # (y0, y1, x0, x1)
    def get_coords(self):
        return coords

def digit_variance(digit, delta):
    coords = digit.coords
    y0 = coords[0]
    y1 = coords[1]
    x0 = coords[2]
    x1 = coords[3]

    h, w = digit.screen.shape[:2]

    more_digits = []
    # variance along x axis
    for x in range (-1*delta, delta, 1):
        if x1+x > w:
            break
        crop = digit.screen[y0:y1, x0+x:x1+x]
        more_coords = (y0, y1, x0+x, x1+x)
        more_digit = Digit(digit.screen, crop, more_coords)
        more_digits.append(more_digit)
        

    return more_digits

# sliding window
BLACK = 255
WHITE = 0
def extract_digits(img):

    y_offset_top = 2
    y_offset_bottom = 3
    window_w = WINDOW_MIN
    h, w = img.shape[:2]

    vals = []
    crop_start = []
    # find the coords of the first digit
    digit_start = find_digit_start(img)

    digits = []

    # loop through enitre screen
    for x in range(digit_start, w, window_w):
        digit = Digit(img)
        # digit candidates
        y0 = 0+y_offset_top
        y1 = h-y_offset_bottom
        x0 = x
        x1 = x+window_w
        ret, digit_crop, percent_white = crop_digits(img, y0, y1, x0, x1)
        if ret == 0:
            # digits.append(digit_crop)
            digit.add_crop(digit_crop)
            digit.add_coords((y0, y1, x0, x1))
            digits.append(digit)

    
    # display these digits
    sep_digits = []
    results = []
    for digit in digits:
        # account for variance in digit crops
        more_digits = digit_variance(digit, 2)
        sep_digits.append(more_digits)
        ret = knn(digit.crop, k=5)
        # print('result:', ret)
        results.append(ret)
        date = str(datetime.now())
        name = "screen"+date[:10]+"_"+date[20:]+".jpg"
        # cv2.imshow('digit', digit.crop)
        # cv2.waitKey(0)

    # # go through all the digits and run them through knn
    # print('digit group size', len(sep_digits))
    # for digit_group in sep_digits:
    #     results = []
    #     print('size:', len(digit_group))
    #     for digit in digit_group:
    #         img = digit.crop
    #         cv2.imshow('digit', img)
    #         cv2.waitKey(0)
    #         ret = knn(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY), k=5)
    #         # print(ret)
    #         for val in ret:
    #             results.append(val)

    #     # identify the digit
    #     if len(results) > 0:
    #         try:
    #             print('digit is:',statistics.mode(results))
    #         except statistics.StatisticsError:
    #             print('digit is:',results[0])
    #     # cv2.imshow('digit', digit.crop)
    #     # cv2.waitKey(0)

    return results

# combines values that are close (within 2) to each other into a 1 value average
def condense_list(x):
    index = 0
    res = []
    i = 0
    while i < len(x)-1:
        curr_val = x[i] 
        next_val = x[i+1]
        if abs(curr_val - next_val) <= 2:
            ave = round(float((curr_val+next_val)/2))
            x[i+1] = ave
            x[i] = 0
        i += 1

    for val in x:
        if val != 0:
            res.append(val)

    return np.asarray(res)

# find the first digit
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
    # plt.show()

    # find peak indices
    peak_indices = signal.find_peaks_cwt(y, np.arange(1,10))
    # print(peak_indices)

    # the 2nd index is the first peak aka first digit
    # return peak_indices[1:]
    return condense_list(peak_indices[1:])[0]

def to_vol_measurement(scale_reading, decimal_pos):
    # this particular scale has a decimal after the 3rd digit from the right
    factor = 10**decimal_pos
    val = 0
    for digit in scale_reading:
        val = val*10 + digit

    # vol in micro liters
    return val

def read_scale(img):
    return to_vol_measurement(extract_digits(img), 3)

if __name__ == '__main__':
    img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/screen" 
    screen_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/crops"
    normed_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/norms"
    
    # load img digit key from json file
    os.chdir(img_dir)
    with open('key.json') as json_data:
        key = json.load(json_data)
  
    # # check_screen_extraction(img_dir)
    # w, h = get_screen_info(screen_dir)
    # aspect = float(w/h)
    # # print(aspect)

    # normalize_screens(screen_dir, aspect)
    os.chdir(normed_dir)
    success = 0
    total = 0
    for file in glob.glob('*.jpg'):
        img = cv2.imread(file)
        # img = cv2.imread('screen2017-08-04_249038.jpg')
        # cv2.imshow('orig', img)
        # extract_digits(img)
        results = read_scale(img)
        print('expected:',key[file],'got:',results)
        if key[file] == str(results):
            success += 1
        total += 1
        
    print('success rate:', float(success/total))






