import sys
import ezdxf
import os
import pprint
import math
from beam_handler import get_beams

file_path = 'Algorithms/LineBWRectangleAlgo/input/DXF/'
input_file = 'extended_lines.dxf' #'beam_testing_edge_cases.dxf'
output_file_path = 'Algorithms/LineBWRectangleAlgo/output/'
input_file_name = input_file.split('.')[0]
output_file = f'{input_file_name}_output.dxf'

# Reading the file
try:
    dwg = ezdxf.readfile(file_path + input_file)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

msp = dwg.modelspace()
print(f'File read success from {file_path}.')    

# Testing on a new file:
# dwg = ezdxf.new()
# msp = dwg.modelspace()
# dwg.layers.new('BEAM')
# lines = (
#     [(430867.3634172502, -4231.230651325338), (430904.8634172497, -4243.230651325519)], 
#     [(431327.1134172498, -4243.194620173659), (431363.1134172497, -4243.194620173659)]
# )
# msp.add_line(lines[0][0], lines[0][1], dxfattribs = {'layer': 'BEAM'})
# msp.add_line(lines[1][0], lines[1][1], dxfattribs = {'layer': 'BEAM'})
# dwg.saveas(file_path + 'sample_file.dxf')
# print(f'SUCCESS in saving INPUT file. at {file_path + "sample_file.dxf"}')

inch_conversion_factor = 0.0393701
mm_conversion_factor = 1.0

beams = get_beams(msp, dwg, 'SHT. BEAM', mm_conversion_factor, output_file_path + output_file)
print(f'Sucess in')
print(f'\n\n**Beams: {beams}')