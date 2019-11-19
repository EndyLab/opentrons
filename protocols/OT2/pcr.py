# imports
from opentrons import labware, instruments

# metadata
metadata = {
    'protocolName': 'Phusion Master Mix PCR',
    'author': 'Anton Jackson-Smith <acjs@stanford.edu>',
    'description': 'Dilute stock primers from 100 uM down to 10 uM for use in a PCR reaction',
}

# design constants

REACTIONS = [
  # DNA: (Forward, Reverse)
  'p70a-deGFP', 1, 4,
  'p70a-deGFP', 2, 4,
  'p70a-deGFP', 3, 4,
]

DNA_VOLUME = 1
PCR_VOLUME = 50

# labware
racks = {
  '300ul': [labware.load('opentrons-tiprack-300ul', '7')],
  '10ul': [labware.load('opentrons-tiprack-10ul', '8')]
  }

stocks = labware.load('opentrons_24_tuberack_generic_2ml_screwcap', '3')
pcr_tubes = labware.load('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '2')

water_stock = stocks['A1']
pcr_master_mix = stocks['A2']

primer_stocks = {
    1: pcr_tubes['B1'],
    2: pcr_tubes['B2'],
    3: pcr_tubes['B3'],
    4: pcr_tubes['B4'],
}

dna_stocks = {
    'p70a-deGFP': stocks['C1'],
    'pSB1C3-sfGFP': stocks['C2']
}

target_tubes = pcr_tubes

# pipettes
p50 = instruments.P50_Single(mount='left', tip_racks=racks['300ul'])
p10 = instruments.P10_Single(mount='right', tip_racks=racks['10ul'])

# commands

# build pcr
primer_vol = PCR_VOLUME / 20
mastermix_vol = PCR_VOLUME / 2
water_vol = PCR_VOLUME - mastermix_vol - primer_vol*2 - DNA_VOLUME

num_reactions = len(REACTIONS)

p50.distribute(water_vol, water_stock, [pcr_tubes[i] for i in range(num_reactions)])
p50.distribute(mastermix_vol, pcr_master_mix, [pcr_tubes[i] for i in range(num_reactions)])

for i, (dna, fwd, rev) in REACTIONS.enumerate():
    p10.transfer(DNA_VOLUME, dna_stocks[dna], target_tubes[i], mix_before=(2, DNA_VOLUME), mix_after=(3, DNA_VOLUME))
    p10.transfer(primer_vol, primer_stocks[fwd], target_tubes[i], mix_before=(2, primer_vol), mix_after=(3, primer_vol))
    p10.transfer(primer_vol, primer_stocks[rev], target_tubes[i], mix_before=(2, primer_vol), mix_after=(3, primer_vol))
