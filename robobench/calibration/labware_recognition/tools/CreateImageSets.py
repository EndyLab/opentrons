from os import listdir 
from os.path import join

annotation_dir = '../models/object_detection/VOCdevkit/VOC2012/Annotations'
main_dir = '../models/object_detection/VOCdevkit/VOC2012/ImageSets/Main'
image_dir = '../models/object_detection/VOCdevkit/VOC2012/JPEGImages'

classes = ['96wellplate', 'scale', 'tiprack', 'trough', 'trash']
robots = ['hiro', 'enzo']
slots = ['A1', 'A2', 'A3',
		'B1', 'B2', 'B3',
		'C1', 'C2', 'C3',
		'D1', 'D2', 'D3',
		'E1', 'E2', 'E3']

train_class_files = [open(join(main_dir, class_type + '_train.txt'), 'w') for class_type in classes]
val_class_files = [open(join(main_dir, class_type + '_val.txt'), 'w') for class_type in classes]


def createImageSet():
	# Assumes files are formatted as in LabImageCapture.py
	# Generates 
	annotation_files = [f for f in listdir(annotation_dir) if not f.startswith('.')]
	for filename in annotation_files:
		print(filename)
		object_type, robot, slot, purpose = filename.split('-')[0].split('_')
		if purpose == 't':
			print('train')
			curr_files = train_class_files
		else:
			print('eval')
			curr_files = val_class_files
		for i in range(len(classes)):
			if classes[i] == object_type:
				curr_files[i].write(filename[:-4] + ' 1\n')
			else:
				curr_files[i].write(filename[:-4] + ' -1\n')

if __name__ == '__main__':
	createImageSet()