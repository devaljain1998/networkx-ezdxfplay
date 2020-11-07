import sys
import ezdxf
from clean_wall_lines import get_cleaned_wall_lines

# Wall line test-case:
# wall_lines = [
#     [(0, 4), (4, 4)],
#     [(4, 4), (4, 0)],
#     [(4, 0), (6, 0)],
#     [(6, 0), (6, 6)],
#     [(6, 4), (8, 4)],
#     [(8, 4), (8, 0)],
#     [(8, 0), (10, 0)],
#     [(10, 0), (10, 6)],
#     [(10, 6), (6, 6)],
#     [(6, 6), (0, 6)],
# ]

# Now testing on the actual file
file_path = 'dxfFilesIn/dxf_files/'
input_file = 'detect_wall.dxf'
output_file_path = 'dxfFilesOut/'
input_file_name = input_file.split('.')[0]
output_file = f'{input_file_name}_output.dxf'

# Reading the file
try:
    dwg = ezdxf.readfile(file_path + input_file)
except IOError:
    print(f'Not a DXF file or a generic I/O error.', file_path + input_file)
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

msp = dwg.modelspace()
print(f'File read success from {file_path}.')    


wall_layer = 'WALL'
def get_wall_lines():
    dxf_wall_lines = msp.query(f'LINE[layer=="{wall_layer}"]')
    wall_lines = []
    # cleaning lines
    for line in dxf_wall_lines:
        try:
            x1, y1, z1 = line.dxf.start
            x2, y2, z2 = line.dxf.end
        except Exception as e:
            print(f'Exception occured while reading line: {e}')
            continue
            
        wall_line = [(x1, y1), (x2, y2)]
        wall_lines.append(wall_line)
            
    return wall_lines

wall_lines = get_wall_lines()
from pprint import pprint
print('wall_lines: ', len(wall_lines))

cleaned_wall_lines = get_cleaned_wall_lines(wall_lines)
pprint(cleaned_wall_lines)