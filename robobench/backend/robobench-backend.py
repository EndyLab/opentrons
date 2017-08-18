from flask import Flask, jsonify
from flask import render_template, request
from protocol_transfer import transfer

CURRENT_VOL = 0
app = Flask(__name__)

def get_labware():
    return {
        'A1': 'WellPlate',
        'C2': 'WellPlate',
        'B3': 'Trash',
        'B2': 'WellPlate',
        'E3': 'Trash',
        'D3': 'WellPlate'
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


"""
    Usage:
    ----------------
    pipette: the pipette that transfers liquid
    source: tuple of source container type and slot Ex: () well, A1 )
    dest: destination plate
    wells: dictionary of wells to transfer stuff to asusming 1:1 well transfer ratio here
    vol: volume to transfer (1 volume for now MVP)
    96-flate the pipette gets its tips from
    water: where the water is 
"""
# def transfer(pipette, source_dict, dest_dict, wells, vol):
    # source = calibrateToSlot(source_dict[0], 'source', source_dict[1], pipette)
    # dest = calibrateToSlot(dest_dict[0], 'dest', dest_dict[1], pipette)

    # # wells will be in form {source, dest}
    # for key, value in wells.items(): 
    #     # aspirate from source
    #     pipette.aspirate(vol, source.wells(key))

    #     # dispense to dest
    #     pipette.dispense(dest.wells(value))


# setting the volume
@app.route('/volume', methods=['POST'])
def volume():
    if request.method == 'POST':
        volume = request.form['volume']
        CURRENT_VOL = volume
        print(CURRENT_VOL)
        return volume

# @app.route('/transfer/<pipette')
# def run_transfer(pipette, source_dict, dest_dict, wells, vol):
#     transfer(pipette, source_dict, dest_dict, wells, vol)
