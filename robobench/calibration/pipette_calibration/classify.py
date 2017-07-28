import cv2
import numpy as np

# classifies an array of imgs
def knn(imgs, k=2):
	# load the data we generated previously
	training_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/training" 
	samples = np.loadtxt(training_dir+'/general-samples.data').astype(np.float32)
	responses = np.loadtxt(training_dir+'/general-responses.data').astype(np.float32)
	responses = responses.reshape((responses.size,1))

	# train the KNN model
	knn_model = cv2.ml.KNearest_create()
	knn_model.train(samples,cv2.ml.ROW_SAMPLE,responses)
	identified = []
	for img in imgs:
		img_scaled = cv2.resize(img, (10,25))
		sample = img_scaled.reshape((1,250))
		sample = np.float32(sample)
		ret, results, neighbours, dist = knn_model.findNearest(sample, k)
		identified.append(int(results[0][0]))

	return identified


if __name__ == '__main__':
	training_dir = "C:/Users/gohna/Documents/bioe reu/opentrons/robobench/calibration/pipette_calibration/training" 

	# load the data we generated previously
	samples = np.loadtxt(training_dir+'/general-samples.data').astype(np.float32)
	responses = np.loadtxt(training_dir+'/general-responses.data').astype(np.float32)
	responses = responses.reshape((responses.size,1))

	# train the KNN model
	print("sample size", samples.shape,"response size:",responses.size)
	knn_model = cv2.ml.KNearest_create()
	knn_model.train(samples,cv2.ml.ROW_SAMPLE,responses)

	test = training_dir + '/9/DIGIT120207.jpg'
	img = cv2.imread(test)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img_scaled = cv2.resize(img, (10, 25))
	print(img_scaled.shape)
	sample = img_scaled.reshape((1,250))
	sample = np.float32(sample)
	print("img test size", sample.shape)
	ret, results, neighbours, dist = knn_model.findNearest(sample, k=2)
	matches = results==responses
	string = str(int((results[0][0])))
	# print(matches)
	print(string)