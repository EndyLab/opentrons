import cv2
import numpy as np
from matplotlib import pyplot as plt
import glob, os

def img_to_digit(img, templates):
    imgW, imgH = img.shape[::-1]
    # print("height", imgH, "width",imgW)
    figX = 3
    figY = 10
    identified = []
    # loop through templates 0-9
    for i, template in enumerate(templates):
        # template = cv2.imread(template_name,0)
        cv2.imshow('template',template)
        w, h = template.shape[::-1]
        print("height", h, "width",w)

        # make sure template height is not bigger than img height
        if imgH < h:
            r = float(h/imgH)
            img = cv2.resize(img,None,fx=r,fy=r,interpolation=cv2.INTER_LINEAR)


        res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
        # When using cv2.TM_CCOEFF_NORMED max_loc will be the location of the 
        # template in your img. And max_val will be the correlation of the match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print("digit:",i,"corr:",max_val)
        threshold = 0.6
        loc = np.where( res >= threshold)
        backtorgb = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        # draw rectangle
        # for pt in zip(*loc[::-1]):
        if max_val >= threshold:
            cv2.rectangle(backtorgb, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,0,255), 1)
        # (digit, corr, pts)
        # temp = (i, max_val, pt)
        # identified.append(temp)

        plt.subplot(figY,figX,i*figX+1),plt.imshow(template,cmap = 'gray')
        plt.xticks([]), plt.yticks([])
        plt.subplot(figY,figX,i*figX+2),plt.imshow(res,cmap = 'gray')
        plt.title(str(max_val))
        plt.xticks([]), plt.yticks([])
        plt.subplot(figY,figX,i*figX+3),plt.imshow(backtorgb,cmap = 'gray')
        plt.xticks([]), plt.yticks([])
        cv2.imshow('matched!!!',backtorgb)
    plt.show()
    return identified

# main function
if __name__ == '__main__':
    img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/test_imgs" 
    template_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/templates" 

    templates = []
    bin_imgs = []

    os.chdir(template_dir)
    for file in glob.glob("*.jpg"):
        # templates
        # print(file)
        if 'template' in file:
            templates.append(template_dir+'/'+str(file))

    os.chdir(img_dir)
    for file in glob.glob("*.jpg"):
        # test files
        # print(file)
        if 'bin' in file:
            bin_imgs.append(img_dir+'/'+str(file))

    figX = 3
    figY = 10

    for img_name in bin_imgs:
        img = cv2.imread(img_name,0)
        cv2.imshow('img',img)
        imgW, imgH = img.shape[::-1]



        print("height", imgH, "width",imgW)
        # loop through templates 0-9
        for i, template_name in enumerate(templates):
            template = cv2.imread(template_name,0)
            cv2.imshow('template',template)
            w, h = template.shape[::-1]
            # print("TEMPLATE height", h, "width",w)

            # make sure template height is not bigger than img height
            if imgH < h:
                r = float(h/imgH)
                img = cv2.resize(img,None,fx=r,fy=r,interpolation=cv2.INTER_LINEAR)


            res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
            threshold = 0.6
            loc = np.where( res >= threshold)
            backtorgb = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

            # draw rectangle
            for pt in zip(*loc[::-1]):
                cv2.rectangle(backtorgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 1)

            plt.subplot(figY,figX,i*3+1),plt.imshow(template,cmap = 'gray')
            plt.title('template'), plt.xticks([]), plt.yticks([])
            plt.subplot(figY,figX,i*3+2),plt.imshow(res,cmap = 'gray')
            plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            plt.subplot(figY,figX,i*3+3),plt.imshow(backtorgb,cmap = 'gray')
            plt.title('Detected Point'), plt.xticks([]), plt.yticks([])

            cv2.imshow('matched!!!',backtorgb)
        plt.show()
    cv2.waitKey(0)
    cv2.destroyAllWindows()