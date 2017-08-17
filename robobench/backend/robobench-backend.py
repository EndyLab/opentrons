from flask import Flask, jsonify
app = Flask(__name__)

def get_labware():
    return {
        'A1': 'WellPlate',
        'C2': 'WellPlate',
        'B1': 'WellPlate'
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
