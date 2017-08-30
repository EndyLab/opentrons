from protocols import web_transfer1
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import sys

sys.path.append("../calibration/labware_recognition/testing")

# import RobotVision3

app = Flask(__name__)
CORS(app)

# janky way of reducing refreshes for get_labware
get_labware_count = 0
name_to_slot_coord_dict = {}

# janky way to "record procedures"
LAMBDA_QUEUE = []
RECORD = False
# vision = RobotVision3.RobotVision()

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
        'TipRack' : [ ('A2', (23, 45, 10)), ('E3', (0,0,0))],
    }
def get_labware():
    # global get_labware_count, name_to_slot_coord_dict
    # if get_labware_count % 30 == 0:
    #     print("Vision")
    #     name_to_slot_coord_dict = vision.evaluate_deck()
    # print("Get labware")
    # print(name_to_slot_coord_dict)
    # get_labware_count = get_labware_count + 1
    # return name_to_slot_coord_dict


    # TESTING 
    # return hardcode()
    return hardcode_vision()



@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/grid')
def grid():
    response = jsonify({
        'labware_data': get_labware()
    })

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

#  example data from website
SAMPLE = {
    'source': {
        'labware': 'WellPlate', 
        'wells': ['E11'], 
        'slot': 'A1',
        'coords': [1,2,3]
    }, 
    'parameters': {'volume': '78'}, 
    'protocol': 'transfer', 
    'dest': {
        'labware': 'WellPlate', 
        'wells': ['C8'], 
        'slot': 'C1',
        'coords': [1,2,3]
    }, 
    'tiprack': {'labware': 'TipRack'}
}

# runs a lambda protocol from a dict of data
def run_lambda_protocol(data):
    protocol_name = data['protocol']
    volume = data['parameters']['volume']

    protocolDict = {
        'transfer': lambda: web_transfer1(data),
        'dilution': lambda: web_transfer1(data),
    }
    protocolDict[protocol_name]()

@app.route('/run', methods=['POST'])
def run():
    print("Run pressed")
    # return response
    data = request.get_json()
    # print("DATA:", data)

    # check that same number of wells are selected
    # if len(data['source']['wells']) != len(data['dest']['wells']):
    #     response = jsonify({
    #         'status': 'bad well(s) input'
    #     })
    #     return response

    # check if protocols should be recorded
    # global RECORD
    # if RECORD == True:
    #     # temp = lambda: web_transfer(data['source'], data['dest'], data['volume'])
    #     LAMBDA_QUEUE.append(data)

    # print("protocol LIST: ", LAMBDA_QUEUE)
    run_lambda_protocol(data)

    response = jsonify({
        'status': 'ok'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# record user protocol stack
@app.route('/record', methods=['POST'])
def record():
    data = request.get_json()
    global RECORD
    RECORD = data['record']
    # print(data, RECORD)

    response = jsonify({
        'status': 'ok'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def run_lambda_queue():
    global LAMBDA_QUEUE
    for data in LAMBDA_QUEUE:
        run_lambda_protocol(data)

# save a protocol top the stack
@app.route('/record/save', methods=['POST'])
def record_save():
    print("python responding to button press, ACTION: saving protocols")

    # gets protocol data from frontend
    data = request.get_json()
    # print(data)
    # global RECORD
    # if RECORD == True:
    # temp = lambda: web_transfer(data['source'], data['dest'], data['volume'])
    global LAMBDA_QUEUE
    LAMBDA_QUEUE.append(data)
    response = jsonify({
        # 'status': 'ok',
        'lambdas': LAMBDA_QUEUE
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# run user defined protocol stack
@app.route('/record/run')
def record_run():
    print("hi running record button hit")
    # data = request.get_json()
    # if data['running_record'] == True:
    run_lambda_queue()

    response = jsonify({
        'status': 'ok'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# returns the list of protocols so frontend can display 
@app.route('/record/show')
def record_show():
    print("hi showing recording functions")
    # print(LAMBDA_QUEUE)
    
    response = jsonify({
        # 'status': 'ok',
        'lambdas': LAMBDA_QUEUE
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/record/clear')
def record_clear():
    print("hi clearing protocol list now")
    global LAMBDA_QUEUE
    LAMBDA_QUEUE = []
    response = jsonify({
        # 'status': 'ok',
        'lambdas': LAMBDA_QUEUE
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/record/update', methods=['POST'])
def record_update():
    data = request.get_json()

    global LAMBDA_QUEUE
    LAMBDA_QUEUE = data

    print("UPDATING LAMBDAS")
    # print(data)
    response = jsonify({
        # 'status': 'ok',
        'lambdas': LAMBDA_QUEUE
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__== "__main__":
    app.run(host='0.0.0.0')