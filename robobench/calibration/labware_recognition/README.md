# Labware Recognition Pipeline
Steps to use TensorFlow's Object Recognition Pipeline
**Still need to run through steps and debug**

![alt text](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/examples/deckrecognition.png)

**Resources**:
[TensorFlow Object Detection Documentation](https://github.com/tensorflow/models/tree/master/object_detection)
[Useful StackOverflow post](https://stackoverflow.com/questions/44973184/train-tensorflow-object-detection-on-own-dataset/) documenting steps

This document is an add on to these resources to help you train for labware detection more easily.

## Installations

Install TensorFlow https://www.tensorflow.org/install/

Clone TensorFlow models repo to this folder (labware_recognition) https://github.com/tensorflow/models

Install Object Detection API https://github.com/tensorflow/models/blob/master/object_detection/g3doc/installation.md
(Do not forget the protobuf and path steps)

## Building Data Set

Before beginning, I would recommend completing the first object detection tutorial and looking through the SO post and the second object detection tutorial.

Within models/object_detection, create the following directory structure:
```
+VOCdevkit
  +VOC2012
    +Annotations
    +ImageSets
      +Main
    +JPEGImages
```

All training and validation images should be placed in JPEGImages.

To capture labware images, can use [LabImageCapture.py](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/tools/LabImageCapture.py)
**Note:** opencv3 version 3.0.0 should be used for OSX, the most recent version crashes with video capture. To install, see https://anaconda.org/jlaura/opencv3


### Create PASCAL VOC Dataset

Follow instructions from the StackOverflow [post](https://stackoverflow.com/questions/44973184/train-tensorflow-object-detection-on-own-dataset/44973203#44973203)

Images can be annotated with PASCALVOC format using [labelImg](https://github.com/tzutalin/labelImg)

Once all annotations and images are finalized (see changing test/validation category), [CreateImageSets.py](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/tools/CreateImageSets.py) can be used from tools to generate image scripts if filenames are formatted as in LabImageCapture.py.



#### Changing test/validation category
NEED TO LOOK INTO HOW MERGED DATASET WORKS

You may have some images you intended to use for training that you want to change to validation or vice versa. It is important to alter all the relevant elements of the xml file to be aligned. 

[Sample XML file](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/examples/96wellplate_enzo_A3_t-0.xml)

### Creating TFRecords

If using folder structure described here, change line 84
`img_path = os.path.join(data['folder'], image_subdirectory, data['filename'])`
to
`img_path = os.path.join('VOC2012', image_subdirectory, data['filename'])`

Make sure protoc and PATH steps from installation have been completed.

Then follow instructions in the StackOverflow post.

### Configure Pipeline and Train

Make sure preferred model has been downloaded from [model zoo](https://github.com/tensorflow/models/blob/master/object_detection/g3doc/detection_model_zoo.md). We have been using ssd_mobilenet_v1_coco. Folder should be placed in models/object_detection

I would recommend running locally to debug before pushing to the cloud. TF provides good documentation, the pets tutorial is bascially what we will ultimately do except with the labware dataset.

Contact Anton for access to the lab Google Cloud.

