from pprint import pprint
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
    'main': 'detect_wall.dxf',
    'sample': 'Sample.dxf',
    'sample2': 'sample2.dxf',
    'sample3': 'sample3.dxf',
    'sample4': 'sample4.dxf',
    'sample5': 'sample5.dxf',
    'sample6': 'sample6.dxf',
    'sample7': 'sample7.dxf',
    'sample8': 'sample8.dxf',
    'sample10': 'sample10.dxf',
    
    # p20 files:
    'p20_ground_floor': 'p20_ground_floor.dxf',
    'p20_first_floor': 'p20_first_floor.dxf',
    'p22_ground_floor': 'p22_ground_floor.dxf',
    'p22_first_floor': 'p22_ground_floor.dxf',
    'p23_ground_floor': 'p23_ground_floor.dxf',
    'p23_first_floor': 'p23_first_floor.dxf',    
}
input_key = 'p20_ground_floor'
input_file = input_files[input_key]

base_output_file_path = f'dxfFilesOut/{input_key}/'
output_file_path = f'dxfFilesOut/{input_key}/debug_dxf/'
# Checking and creating a directory for the output filepath
try:
    import pathlib
    current_file_path = str(pathlib.Path(
        __file__).parent.absolute()) + '/' + base_output_file_path
    path_to_be_created = os.path.join(current_file_path, 'debug_dxf')
    mode = 0o777
    os.mkdir(path_to_be_created, mode)
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


wall_layers = {'main': 'WALL', 'sample': 'WALLS',
               'sample2': 'WALLS', 'sample3': 'WALLS',
               'sample4': 'PP-WALL', 'sample5': 'PP-WALL', 
               'sample6': 'PP-WALL', 'sample7': 'PP-WALL', 
               'sample8': 'PP-WALL', 'sample9': 'PP-WALL', 
               'sample10': 'PP-WALL',
               
               # p20 files
               'p20_ground_floor': 'PP-Wall',
               'p20_first_floor': 'PP-Wall',
               'p22_ground_floor': 'PP-Wall',
               'p22_first_floor': 'PP-Wall',
               'p23_ground_floor': 'PP-Wall',
               'p23_first_floor': 'PP-Wall',
               }

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
print('wall_lines: ', len(wall_lines))

# testing components:
# dwg.layers.new('comp_debug_text')
# draw_components(wall_lines, msp, dwg)
# dwg.saveas(output_file_path + output_file)
# print(f'Success in saving {output_file_path + output_file} for testing components.')


# Operations:
cleaned_wall_lines, graph = get_cleaned_wall_lines(
    wall_lines, filepath=output_file_path)
pprint(cleaned_wall_lines)
print('edges: ', list(graph.edges))
print(len(graph.edges))

# Now getting centrelines from the wall_lines:
conversion_factor = {
    'mm': 1.0,
    'inch': 0.0393701
}
centre_lines = get_centre_lines(
    msp, dwg, "", conversion_factor=conversion_factor['inch'],
    lines = cleaned_wall_lines)
# pprint([centre_line.__dict__ for centre_line in centre_lines])

#### POC OPERATIONS:
from test_shapely import extend_wall_lines_for_entity, get_area_from_the_room_texts, fill_str_tree
import json
counter = 0
def test_shapely():
    try:
        with open(f'dxfFilesIn/identification_json/{input_key}.json') as identification_json_file:
            identification_json = json.load(identification_json_file)
            print('Success in reading the JSON file.')
    except Exception:
        print('Failed to open identification JSON.')

    windows = list(filter(lambda entity: entity['type']=='window' and entity['category'] == 'p', identification_json['entities']))
    doors = list(filter(lambda entity: entity['type']=='door' and entity['category'] == 'p', identification_json['entities']))
    
    print('windows', len(windows))
    print('doors', len(doors))

    fill_str_tree(centre_lines=centre_lines)

    global counter
    for counter, current_entity in enumerate(windows):
        # DEBUG
        print('COUNTER', counter)
        
        if input_key == 'sample3' and counter in [6]:
            continue
        
        extend_wall_lines_for_entity(entity=current_entity, centre_lines=centre_lines, graph=graph, input_key=input_key, counter=counter)

        print('Now plotting on msp', counter)
        dwg = ezdxf.new()
        msp = dwg.modelspace()

        for edge in graph.edges():
            msp.add_line(edge[0], edge[1])
        msp.add_circle(current_entity['location'], radius=2)

        dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')
        print('saved: ', f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')

    window_counter = counter   
    print('WINDOWS COMPLETE!!\n')
    # Now iterating for doors
    for counter, current_entity in enumerate(doors):
        counter = window_counter + counter + 1
        # DEBUG
        print('COUNTER', counter)
        
        try:
            extend_wall_lines_for_entity(entity=current_entity, centre_lines=centre_lines, graph=graph, input_key=input_key, counter=counter)
        except Exception as e:
            raise e;
            # continue
            exit()

        print('Now plotting on msp', counter)
        dwg = ezdxf.new()
        msp = dwg.modelspace()

        for edge in graph.edges():
            msp.add_line(edge[0], edge[1])
        msp.add_circle(current_entity['location'], radius=2)

        dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')
        print('saved: ', f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')

    print('extra_data')
    # pprint(extra_data)
    print('Success.')



test_shapely()