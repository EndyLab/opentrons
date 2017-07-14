import cv2
from matplotlib import pyplot as plt
from dipdigits import binarize_img_dir
from digitmatch import img_to_digit
import glob, os

img_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/test_imgs" 
template_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/templates" 

# generate binaries
bimgs = binarize_img_dir(img_dir)
for i, img in enumerate(bimgs):
	plt.subplot(3,3,i+1),plt.imshow(img,cmap = 'gray')
	plt.title("binary img"+str(i))
	plt.xticks([]),plt.yticks([])
	# cv2.imshow(str(i), img)
plt.show()

# digit matching
# get templates
template_imgs = []
os.chdir(template_dir)
for file in glob.glob("*.jpg"):
    # templates
    if 'template' in file:
    	name = template_dir+'/'+str(file)
    	template = cv2.imread(name,0)
    	template_imgs.append(template)


for img in bimgs:
	img_to_digit(img, template_imgs)

cv2.waitKey(0)
cv2.destroyAllWindows()