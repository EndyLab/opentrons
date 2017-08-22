from protocols import web_transfer
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import sys

sys.path.append("../calibration/labware_recognition/testing")

# import RobotVision

app = Flask(__name__)
CORS(app)

# janky way of reducing refreshes for get_labware
get_labware_count = 0
slot_to_name_dict = {}

def get_labware():
    # global get_labware_count, slot_to_name_dict
    # if get_labware_count % 30 == 0:
    #     print("Vision")
    #     slot_to_name_dict = RobotVision.evaluateDeckSlots()
    # print("Get labware")
    # print(slot_to_name_dict)
    # get_labware_count = get_labware_count + 1
    # return slot_to_name_dict

    return {
        'A1':'WellPlate',
        'C1':'WellPlate'
    }


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
    # if len(data['source']['wells']) != len(data['dest']['wells']):
    #     response = jsonify({
    #         'status': 'bad well(s) input'
    #     })
    #     return response

    # import time; time.sleep(5);
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
