from protocol_transfer import web_transfer
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import sys

sys.path.append("../calibration/labware_recognition/testing")

<<<<<<< Updated upstream
import RobotVision
=======
import RobotVision3
>>>>>>> Stashed changes

app = Flask(__name__)
CORS(app)

# janky way of reducing refreshes for get_labware
get_labware_count = 0
<<<<<<< Updated upstream
slot_to_name_dict = {}
=======
name_to_slot_coord_dict = {}

# janky way to "record procedures"
LAMBDA_QUEUE = []
RECORD = False
vision = RobotVision3.RobotVision()

def hardcode():
    return {
        'A1':'WellPlate',
        'C1':'WellPlate',
        'C3':'TipRack',
        'B2':'WellPlate',
    }

def hardcode_vision():
    return {
        'WellPlate' : [('A1', (30, 30, 20)), ('B2', (100, 20, 0))],
        'TipRack' : [ ('A2', (23, 45, 10))],
    }
def get_labware():
    global get_labware_count, name_to_slot_coord_dict
    if get_labware_count % 30 == 0:
        print("Vision")
        name_to_slot_coord_dict = vision.evaluate_deck()
    print("Get labware")
    print(name_to_slot_coord_dict)
    get_labware_count = get_labware_count + 1
    return name_to_slot_coord_dict


    # TESTING 
    # return hardcode()
    #return hardcode_vision()

>>>>>>> Stashed changes

def get_labware():
    global get_labware_count, slot_to_name_dict
    if get_labware_count % 30 == 0:
        print("Vision")
        slot_to_name_dict = RobotVision.evaluateDeckSlots()
    print("Get labware")
    print(slot_to_name_dict)
    get_labware_count = get_labware_count + 1
    return slot_to_name_dict
    # return {'A1':'WellPlate',
    #         'B2':'WellPlate'}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/grid')
def grid():
    response = jsonify({
        'labware': get_labware()
    })

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/run', methods=['POST'])
def run():
    print("Run pressed")
    # return response
    data = request.get_json()

    # check that same number of wells are selected
    if len(data['source']['wells']) != len(data['dest']['wells']):
        response = jsonify({
            'status': 'bad well(s) input'
        })
        return response

    # add volume
    data.update({'volume': 100})
    print(request.data)

    web_transfer(data['source'], data['dest'], data['volume'])

    response = jsonify({
        'status': 'ok'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__== "__main__":
    app.run(host='0.0.0.0')
