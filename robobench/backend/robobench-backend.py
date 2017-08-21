from protocol_transfer import web_transfer
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

def get_labware():
    labwareDict = {
        "96-flat": "WellPlate",
    }
    return {
        'A1': 'WellPlate',
        'B1': 'WellPlate',
        'D2': 'TipRack',
        'C3': 'Trash',
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
