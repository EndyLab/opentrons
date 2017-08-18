from protocol_transfer import web_transfer
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

def get_labware():
    return {
        'A1': 'WellPlate',
        'C2': 'WellPlate',
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

TEST =  {
            "protocol": "transfer",
            "volume": 10,
            "source": {
                "labware":"WellPlate",
                "slot":"A1",
                "wells":["A1","A2","A3"]
            },
            "dest": { 
                "labware":"WellPlate",
                "slot":"C2",
                "wells":["B1", "B2", "B3"]
            }
        }

test_data =  {
            "protocol": "transfer",
            "volume": 10,
            "source": {
                "labware":"96-flat",
                "slot":"A1",
                "wells":["A1","A2","A3"]
            },
            "dest": { 
                "labware":"96-flat",
                "slot":"C2",
                "wells":["B1", "B2", "B3"]
            }
        }

@app.route('/run', methods=['POST'])
def run():
    # the dictionary
    # data = request.get_json()
    data = test_data

    # not the same amount of wells selected
    if len(data['source']['wells']) != len(data['dest']['wells']):
        response = jsonify({
            'status': 'bad well(s) input'
        })
        return response

    print(data)

    """
        Usage of transfer.py
        ----------------
        pipette: the pipette that transfers liquid
        source: tuple of source container type and slot Ex: () well, A1 )
        dest: destination plate
        wells: dictionary of wells to transfer stuff to asusming 1:1 well transfer ratio here
        vol: volume to transfer (1 volume for now MVP)
        96-flate the pipette gets its tips from
        water: where the water is 
    """
    web_transfer(data['source'], data['dest'], data['volume'])

    response = jsonify({
        'status': 'ok'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response