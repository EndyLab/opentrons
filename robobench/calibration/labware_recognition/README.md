# Labware Recognition Pipeline
Steps to use TensorFlow's Object Recognition Pipeline

## Installations

Use environment.yml to set up virtual env

Install TensorFlow https://www.tensorflow.org/install/

Clone TensorFlow models repo to desired folder https://github.com/tensorflow/models

Install Object Detection API https://github.com/tensorflow/models/blob/master/object_detection/g3doc/installation.md

## Building Data Set

Take a look at TensorFlow's documentation: https://github.com/tensorflow/models/tree/master/object_detection
Before beginning, I would recommend trying the supplied first tutorial.

These instructions are largely based on https://stackoverflow.com/questions/44973184/train-tensorflow-object-detection-on-own-dataset/44973203#44973203

### Create PASCAL VOC Dataset

Create folder structure

Add images using *script name*

Annotate images using labelImg

Create imageSets using *script name*

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


