# imports
from opentrons import labware, instruments

# metadata
metadata = {
    'protocolName': 'Primer Dilute',
    'author': 'Anton Jackson-Smith <acjs@stanford.edu>',
    'description': 'Dilute stock primers from 100 uM down to 10 uM for use in a PCR reaction',
}

# design constants
NUM_PRIMERS = 8 # How many primers are we diluting?
FINAL_VOLUME = 20 # What is our final volume of primer?

# labware
racks = {
  '300ul': [labware.load('opentrons-tiprack-300ul', '7')],
  '10ul': [labware.load('opentrons-tiprack-10ul', '8')]
  }

stocks = labware.load('opentrons_24_tuberack_generic_2ml_screwcap', '3')
primers = stocks['A1':'A8']
water_stock = stocks['B1']

pcr_tubes = labware.load('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '2')

# pipettes
p50 = instruments.P50_Single(mount='left', tip_racks=racks['300ul'])
p10 = instruments.P10_Single(mount='right', tip_racks=racks['10ul'])

# commands

# load water
water_vol = FINAL_VOLUME / 10 * 9
water_pipette = p10 if water_vol * NUM_PRIMERS <= 10 else p50

water_pipette.distribute(water_vol, water_stock, [pcr_tubes[i] for i in range(NUM_PRIMERS)])

# load and mix primer
primer_vol = FINAL_VOLUME / 10
primer_pipette = p10 if primer_vol <= 10 else p50

for i in range(NUM_PRIMERS):
  primer_pipette.transfer(primer_vol,
                          primers[i].top(),
                          pcr_tubes[i],
                          touch_tip=True,
                          blow_out=True,
                          mix_before=(2, primer_vol),
                          mix_after=(3, primer_vol))
