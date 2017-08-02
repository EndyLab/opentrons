import os
import os.path
import glob
import re
from lxml import etree
import copy

TRAINING_DIR = 'robobench/calibration/labware_recognition/data/training/'
BOUNDING_FILE = 'robobench/calibration/labware_recognition/data/training/deck-annotations.xml'

with open(BOUNDING_FILE) as f:
    tree = etree.parse(f)

# Get an annotation header
header = copy.deepcopy(tree)
for elem in header.xpath('//object'): # + header.xpath('//filename') + header.xpath('//path'):
    elem.getparent().remove(elem)

files = glob.glob(TRAINING_DIR + "*.jpg")
for path in files:
    filename = os.path.basename(path)
    labware, robot, grid, group, index = re.match(r'([A-Za-z0-9]+)_([A-Za-z0-9]+)_([ABCDE][0-9])_([tv])-([0-9]+).*', filename).groups()

    # Find the bounding box that matches our object
    box = copy.deepcopy(tree.xpath('//object/name[text()="{}"]/..'.format(grid.lower()))[0])
    name = box.xpath('name')[0]
    name.text = labware

    root = copy.deepcopy(header)
    anno = root.getroot()
    anno.xpath('//filename')[0].text = filename
    anno.xpath('//path')[0].text = path
    anno.append(box)

    with open(os.path.join(os.path.dirname(path), re.sub(r'jpg$', 'xml', filename)), 'w') as f:
        f.write(etree.tostring(root, pretty_print=True).decode())
