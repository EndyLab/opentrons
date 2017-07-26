from os import listdir
import re
from os.path import join

annotation_dir = '../models/object_detection/VOCdevkit/VOC2012/Annotations'
main_dir = '../object_recog_intro/models/object_detection/VOCdevkit/VOC2012/ImageSets/Main'

classes = ['96wellplate', 'scale', 'tiprack', 'trough', 'arm', 'pipette', 'trash']

train_class_files = [open(join(main_dir, class_type + '_train.txt'), 'w') for class_type in classes]
val_class_files = [open(join(main_dir, class_type + '_val.txt'), 'w') for class_type in classes]

annotation_files = listdir(annotation_dir)

for filename in annotation_files:
	print(filename)
	if 'labimage' in filename:
		print('train')
		curr_files = train_class_files
	else:
		print('val')
		curr_files = val_class_files
	with open(join(annotation_dir, filename), 'r') as f:
		data = f.read()
	for i in range (len(classes)):
		if classes[i] in data:
			curr_files[i].write(filename[:-4] + ' 1\n')
		else:
			curr_files[i].write(filename[:-4] + ' -1\n')



