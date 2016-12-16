
# coding: utf-8

# In[1]:

from opentrons import robot, containers, instruments

tiprack = containers.load('tiprack-200ul', 'B2')
plate = containers.load('96-flat', 'B1')
ddH2O = containers.load('point', 'B3', 'ddH2O-trough')
trash = containers.load('point', 'C2', 'holywastedplasticbatman')


# In[2]:

p200 = instruments.Pipette(
    axis='a',
    max_volume=200,
    min_volume=20,
    tip_racks=[tiprack],
    trash_container=trash,
    channels=8,
    name='p200-8'
)


# In[8]:

robot.home(enqueue=True)

volume = 200 # ul
dilution_frac = 1e-1
rows = plate.rows[:5]

p200.pick_up_tip()
for row in rows[1:]:
    p200.aspirate(volume * (1-dilution_frac), ddH2O)
    p200.dispense(row)
p200.drop_tip()

for source, dest in zip(rows, rows[1:]):
    p200.pick_up_tip()
    p200.mix(3, 200, source)
    p200.aspirate(volume * dilution_frac, source)
    p200.dispense(dest).blow_out().touch_tip()
    p200.drop_tip()

