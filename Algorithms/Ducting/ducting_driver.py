import sys
import ezdxf
import os
import pprint
import math
from ducting_driver import get_ductings

file_path = 'Algorithms/LineBWRectangleAlgo/input/DXF/'
input_file = 'beam.dxf'
output_file_path = 'Algorithms/LineBWRectangleAlgo/output/'
input_file_name = input_file.split('.')[0]
output_file = f'{input_file_name}_output.dxf'

#Reading the file
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

ductings = get_ductings()