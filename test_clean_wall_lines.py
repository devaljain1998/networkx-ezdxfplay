import sys
import os
import ezdxf
from clean_wall_lines import get_cleaned_wall_lines
from test_components import draw_components
from centre_lines import get_centre_lines

# Wall line test-case:
# TC1:
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

# TC2:
# wall_lines = [
#     [],
# ]

# Now testing on the actual file
file_path = 'dxfFilesIn/dxf_files/'
input_files = {
    'main':'detect_wall.dxf',
    'sample': 'Sample.dxf'
}
input_key = 'sample'
input_file = input_files[input_key]

base_output_file_path = f'dxfFilesOut/{input_key}/' 
output_file_path = f'dxfFilesOut/{input_key}/debug_dxf/'
# Checking and creating a directory for the output filepath
try:
    import pathlib
    current_file_path =  str(pathlib.Path(__file__).parent.absolute()) + '/' +base_output_file_path
    path_to_be_created = os.path.join(current_file_path, 'debug_dxf')
    mode = 0o666
    os.mkdir(path_to_be_created, mode);
    print('success in creating new directory')
except OSError as error:
    print('Error in creating directory:')
    print(error)

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


wall_layers = {'main':'WALL', 'sample': 'WALLS'}
def get_wall_lines():
    wall_layer = wall_layers[input_key]
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
        # lambda num: round(num, ndigits=4)
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2)) 
            
        wall_line = [(x1, y1), (x2, y2)]
        wall_lines.append(wall_line)
            
    return wall_lines

wall_lines = get_wall_lines()
from pprint import pprint
print('wall_lines: ', len(wall_lines))

# testing components:
# dwg.layers.new('comp_debug_text')
# draw_components(wall_lines, msp, dwg)
# dwg.saveas(output_file_path + output_file)
# print(f'Success in saving {output_file_path + output_file} for testing components.')
cleaned_wall_lines = get_cleaned_wall_lines(wall_lines, filepath = output_file_path)
# Now getting centrelines from the wall_lines:
conversion_factor = {
    'mm': 1.0,
    'inch': 0.0393701
}
centre_lines = get_centre_lines(
    msp, dwg, "", conversion_factor=conversion_factor['inch'],
    lines = cleaned_wall_lines)
# pprint(cleaned_wall_lines)