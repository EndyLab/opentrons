# Robobench v1

Welcome to RoboBench! We're interested in ways to make lab automation more accessible, so that it can be incorporated into everyday lab workflows rather than only used for large repetitive projects.

## Installation

To install and use the Robobench Alexa/Echo integration, you need to download and set up the code, and set up an Amazon developer account with the appropriate settings.

* Download the code: `git clone git@github.com:EndyLab/opentrons.git`
* Install the required packages: `cd opentrons/robobench; pip install -r requirements.txt`
* Set up an Alexa development environment:
  * Follow the instructions at https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/Flask-Ask-A-New-Python-Framework-for-Rapid-Alexa-Skills-Kit-Development
  * The Amazon intents and utterances are in the robobench/alexa subdirectory.
  * Run `ngrok http 5000` to build a tunnel, and point the Alexa endpoint at the URL it gives you.
* Run the controller locally:
** Set the OpenTrons data directory so we pick up calibration data: `export APP_DATA_DIR=<otone_dir>`. On OS X this is in ~/Library/OT One App 2/otone_data
** Run the controller: `python ./alexa.py`

Note that it is helpful to set up a .py protocol matching the deck layout in alexa.py, so that you can calibrate locations through the app.
