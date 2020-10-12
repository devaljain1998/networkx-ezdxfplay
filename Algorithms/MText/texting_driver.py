import sys
import ezdxf
import os
import pprint
import math
import ezdxf
import json
from ezdxf.math import Vector
from math import *

from pillarplus.math import find_distance, get_angle_between_two_points, directed_points_on_line
from pillarplus.texting import add_text_to_chamber

file_path = 'Algorithms/MText/input/'
input_file = 'TestProjectMM.dxf'
output_file_path = 'Algorithms/MText/output/'
input_file_name = input_file.split('.')[0]
output_file = 'output_TestProjectMM.dxf'

# Reading the DXF file
try:
    dwg = ezdxf.readfile(file_path + input_file)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

# Adding a new layer:
dwg.layers.new('TextLayer')
dwg.layers.new('TextLayerBoundry')

msp = dwg.modelspace()
print(f'DXF File read success from {file_path}.')

# Reading the identification JSON:
json_file_path = 'Algorithms/MText/input/testproject_mm_identification.json'
try:
    with open(json_file_path) as json_file:
        identification_json = json.load(json_file)
except Exception as e:
    print(f'Failed to load identification due to: {e}.')
    sys.exit(1)


MTEXT_ATTACHMENT_POINTS = {
    "MTEXT_TOP_LEFT":	1,
    "MTEXT_TOP_CENTER":	2,
    "MTEXT_TOP_RIGHT":	3,
    "MTEXT_MIDDLE_LEFT":	4,
    "MTEXT_MIDDLE_CENTER":	5,
    "MTEXT_MIDDLE_RIGHT":	6,
    "MTEXT_BOTTOM_LEFT":	7,
    "MTEXT_BOTTOM_CENTER":	8,
    "MTEXT_BOTTOM_RIGHT":	9,
}


entities = identification_json['entities']
params = identification_json["params"]

#ADD TEXT TO CHAMBER DRIVER FUNCTION:
for i in (67, 68, 66):
    entity = entities[i]
    add_text_to_chamber(msp, entity, params)
    
print('Testing add_text_to_chamber SUCCESS!')

# Saving the file:
try:
    dwg.saveas(output_file_path + output_file)
    print(f'Success in saving file: {output_file_path + output_file}')
except Exception as e:
    print(f'Failed to save the file due to the following exception: {e}')
    sys.exit(1)