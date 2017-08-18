from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

def get_labware():
    return {
        'A1': 'WellPlate',
        'C2': 'WellPlate',
        # 'B3': 'Trash',
        # 'B2': 'WellPlate',
        # 'E3': 'Trash'
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
    data = request.get_json()

    print(request.data)
    response = jsonify({
        'status': 'ok'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
