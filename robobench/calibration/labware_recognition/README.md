# Labware Recognition Pipeline
Steps to use TensorFlow's Object Recognition Pipeline
**Still need to run through steps and debug**

![alt text](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/deckrecognition.png)

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

Once all annotations and images are finalized, LINK can be used to generate image scripts if LabImageCapture.py was used to capture the images.

#### Changing test/validation category
ADD LINK TO SAMPLE XML FILE WITH EXPLANATIONS
NEED TO LOOK INTO HOW MERGED DATASET WORKS

You may have some images you intended to use for training that you want to change to validation or vice versa. It is important to alter all the relevant elements of the xml file to be aligned (ADD LINK OF EXAMPLE SCRIPT).

#### Creating TFRS Records

DESCRIBE CHANGE TO TO FOLDER VARIABLE



TF provides a [script](https://github.com/tensorflow/models/blob/master/object_detection/g3doc/preparing_inputs.md) to convert a PASCAL VOC dataset to the desired TFRecords format. This section gives a possible approach to creating a PASCAL VOC dataset.

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
[LabImageCapture.py](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/tools/LabImageCapture.py) can be use to collect the images and place them in the appropriate folder. The script requires opencv and imutils.
**Note:** opencv3 version 3.0.0 should be used for OSX, the most recent version crashes with video capture. To install, see https://anaconda.org/jlaura/opencv3

Annotate images using [labelImg](https://github.com/tzutalin/labelImg)

When completed, make sure to move annotations to Annotations.

Create imageSets using [CreateImageSets.py](https://github.com/EndyLab/opentrons/blob/master/robobench/calibration/labware_recognition/tools/CreateImageSets.py).

Change label map file

### Generate TFRecords

From https://stackoverflow.com/questions/44973184/train-tensorflow-object-detection-on-own-dataset/44973203#44973203:

"If you look into their code especially this line, they explicitly grab the aeroplane_train.txt only. For curios minds, here's why. Change this file name to any of your class train text file.

Make sure VOCdevkit is inside models/object_detection then you can go ahead and generate the TFRecords.

Please go through their code first should you run into any problems. It is self explanatory and well documented."

### Configure Pipeline

Follow instructions here: https://github.com/tensorflow/models/blob/master/object_detection/g3doc/configuring_jobs.md
Sample config files are located in https://github.com/tensorflow/models/tree/master/object_detection/samples/configs

### Training

I found this tutorial https://github.com/tensorflow/models/blob/master/object_detection/g3doc/running_pets.md useful to setting up on the cloud, in addition to the
pages on running locally https://github.com/tensorflow/models/blob/master/object_detection/g3doc/running_locally.md and running
on the cloud https://github.com/tensorflow/models/blob/master/object_detection/g3doc/running_on_cloud.md

*Add lab Google cloud account*


