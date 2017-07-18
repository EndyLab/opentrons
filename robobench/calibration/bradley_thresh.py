# from: https://stackoverflow.com/questions/33091755/bradley-roth-adaptive-thresholding-algorithm-how-do-i-get-better-performance
import numpy as np
from scipy import ndimage
from PIL import Image
import copy
import time
import cv2

def faster_bradley_threshold(image, threshold=75, window_r=5):
    percentage = threshold / 100.
    window_diam = 2*window_r + 1
    # convert image to numpy array of grayscale values
    img = np.array(image.convert('L')).astype(np.float) # float for mean precision 
    # matrix of local means with scipy
    means = ndimage.uniform_filter(img, window_diam)
    # result: 0 for entry less than percentage*mean, 255 otherwise 
    height, width = img.shape[:2]
    result = np.zeros((height,width), np.uint8)   # initially all 0
    result[img >= percentage * means] = 255       # numpy magic :)
    # convert back to PIL image
    return Image.fromarray(result)

def bradley_threshold(image, threshold=75, windowsize=5):
    ws = windowsize
    image2 = copy.copy(image).convert('L')
    w, h = image.size
    l = image.convert('L').load()
    l2 = image2.load()
    threshold /= 100.0
    for y in range(h):
        for x in range(w):
            #find neighboring pixels
            neighbors =[(x+x2,y+y2) for x2 in range(-ws,ws) for y2 in range(-ws, ws) if x+x2>0 and x+x2<w and y+y2>0 and y+y2<h]
            #mean of all neighboring pixels
            mean = sum([l[a,b] for a,b in neighbors])/len(neighbors)
            if l[x, y] < threshold*mean:
                l2[x,y] = 0
            else:
                l2[x,y] = 255
    return image2

if __name__ == '__main__':
    img = Image.open('img_fail.jpg')

    """
    t0 = time.process_time()
    threshed0 = bradley_threshold(img)
    print('original approach:', round(time.process_time()-t0, 3), 's')
    threshed0.show()
    """
    t0 = time.process_time()
    threshed1 = faster_bradley_threshold(img)
    print('w/ numpy & scipy :', round(time.process_time()-t0, 3), 's')

    open_cv_image = np.array(threshed1) 
    cv2.imshow("screen cropped", open_cv_image)
    threshed1.show()

    cv2.waitKey(0)
    cv2.destroyAllWindows()

