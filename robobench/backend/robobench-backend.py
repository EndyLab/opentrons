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

# janky way to "record procedures"
LAMBDA_QUEUE = []
RECORD = False

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

#  example data from website
SAMPLE = {
    'source': {
        'labware': 'WellPlate', 
        'wells': ['E11'], 
        'slot': 'A1'
    }, 
    'parameters': {'volume': '78'}, 
    'protocol': 'transfer', 
    'dest': {
        'labware': 'WellPlate', 
        'wells': ['C8'], 
        'slot': 'C1'
    }, 
    'tiprack': {'labware': 'TipRack'}
}

# runs a lambda protocol from a dict of data
def run_lambda_protocol(data):
    protocol_name = data['protocol']
    volume = data['parameters']['volume']

    protocolDict = {
        'transfer': lambda: web_transfer(data['source'], data['dest'], volume),
        'dilution': lambda: web_transfer(data['source'], data['dest'], volume),
    }
    protocolDict[protocol_name]()

@app.route('/run', methods=['POST'])
def run():
    print("Run pressed")
    # return response
    data = request.get_json()
    print("DATA:", data)

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

    print("protocol LIST: ", LAMBDA_QUEUE)
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
    print(data, RECORD)

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
    print(data)
    # global RECORD
    # if RECORD == True:
    # temp = lambda: web_transfer(data['source'], data['dest'], data['volume'])
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

@app.route('/record/show')
def record_show():
    print("hi showing recording functions")
    # data = request.get_json()
    # if data['running_record'] == True:
    print(LAMBDA_QUEUE)


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

if __name__== "__main__":
    app.run(host='0.0.0.0')