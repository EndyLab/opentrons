import cv2
import glob, os
import numpy as np

training_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/training" 

samples =  np.empty((0, 250))
responses = []

# digits 0-9
for i in range(10):
	print('training digit:',i)
	os.chdir(training_dir+'/'+str(i))
	for file in glob.glob("*.jpg"):
		ratio = 0.2
		img = cv2.imread(file)
		img = cv2.resize(img,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_LINEAR)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		img_scaled = cv2.resize(img, (10, 25))
		# cv2.imshow("small",img_scaled)
		sample = img_scaled.reshape((1,250))
		# cv2.imshow("small resized",sample)

		# save pixel data
		samples = np.append(samples,sample,0)

		# response data
		responses.append(i)

print('training complete')
os.chdir(training_dir)
np.savetxt('general-samples.data', samples)
responses = np.array(responses, np.float32)
responses = responses.reshape((responses.size,1))
np.savetxt('general-responses.data', responses)
cv2.waitKey(0)
cv2.destroyAllWindows()

