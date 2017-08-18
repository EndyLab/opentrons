from protocol_transfer import web_transfer
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

def get_labware():
    return {
        'A1': 'WellPlate',
        'B1': 'WellPlate',
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

if __name__ == '__main__':
    app.run(host='0.0.0.0')