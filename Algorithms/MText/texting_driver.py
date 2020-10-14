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
from pillarplus.texting import add_text_to_chamber, add_text_to_connection, add_text_to_wall, add_text_through_pp_outer, add_text_to_location

file_paths = {
    'wall' : 'Algorithms/MText/input/Deval/TestProjectMM/',#'Algorithms/MText/input/Deval/KHouseIN/'#'Algorithms/MText/input/mm file/',
    'connection' : 'Algorithms/MText/input/Deval/TestProjectMM/'
}
input_files = {
    'wall': 'in.dxf',
    'connection': 'in.dxf'
}
output_files = {
    'wall' : 'output_add_text_through_location_TestProjectMM.dxf',#'output_WALL_KHATRI_TestProjectInch_PPOUTER.dxf'#'output_WALL_KHATRI_TestProjectInch.dxf'
    'connection': 'output_connection_TestProjectMM.dxf'
}

file_path = file_paths['connection'] #'Algorithms/MText/input/'
input_file = input_files['connection'] #'TestProjectInch.dxf'
output_file_path = 'Algorithms/MText/output/'
input_file_name = input_file.split('.')[0]
output_file = output_files['connection'] #'output_TestProjectInch.dxf'

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
json_file_paths = {
    'wall': 'Algorithms/MText/input/Deval/KHouseIN/identification.json',#'Algorithms/MText/mm_identification.json',
    'connection': 'Algorithms/MText/input/Deval/TestProjectMM/khatri_connections_identification.json'
}
json_file_path = json_file_paths['connection'] #'Algorithms/MText/input/TestProject_inch.json'
# json_file_path = 'Algorithms/MText/input/connections_identification.json'
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

# entities = identification_json['entities']
entities = {entity['number']: entity for entity in identification_json['entities']}
# joints = identification_json['joints']
joints = {joint['number']: joint for joint in identification_json['joints']}
connections = identification_json['connections']
params = identification_json["params"]

#ADD TEXT TO CHAMBER DRIVER FUNCTION:
# for i in (18,):
#     entity = entities[i]
#     add_text_to_chamber(msp, entity, params, 'TextLayer')
    
# print('Testing add_text_to_chamber SUCCESS!')

# ADD TEXT TO CONNECTION DRIVER FUNCTION
for connection in connections:
    source = entities.get(connection.get('source_number')) if connection['source_type'] == 'Entity' else joints.get(connection.get('source_number'))
    end = entities.get(connection.get('target_number')) if connection['target_type'] == 'Entity' else joints.get(connection.get('target_number'))
    conncection_start = connection['source_number']
    add_text_to_connection(connection, source['location'], end['location'], params, msp, 'TextingLayer')


# ADD TEXT TO WALL DRIVER FUNCTION
# switch_boards = [i for i in range(12, 24)] #24
# conversion_factor = params['Units conversion factor']
# walls = {wall['number']: wall for wall in identification_json['walls']}
#wall_lights = [5, 12, 13, 14, 19]
# entities_with_walls = list(filter(lambda entity: entity['wall_number'] is not None, entities))
# Testing on entites with walls:
# for entity in entities_with_walls:
#     wall = walls[entity['wall_number']]
#     point = entity['location']
#     add_text_to_wall(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", wall, params, msp, 'TextLayer')


# Testing on wall_lights:
# for i in entities_with_walls: #wall_lights:
#     wall_light = entities[i]
#     wall = walls[wall_light['wall_number']]
#     point = wall_light['location']
#     add_text_to_wall(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", wall, params, msp, 'TextLayer')

# Calling function by hardcoding:
# for i in switch_boards:
#     switch_board = entities[i]
#     wall = list(filter(lambda wall: wall['number'] == switch_board['wall_number'], walls))[0]
#     point = switch_board['location']
#     # print(f'Point: {point}')
#     add_text_to_wall(point, "Hello PillarPlus!\nAnother Line of\nText.", wall, params, msp, 'TextLayer')


# TEST ADD TEXT THROUGH PP OUTER
# for entity in entities:
#     point = entity['location']
#     add_text_through_pp_outer(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", params, msp, 'TextLayer')


# TEST ADD POINT THROUGH LOCATION
# for point in [(0, 0),]:
#     msp.add_circle(point, 2)
#     add_text_to_location(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", pi/4, 0, params, msp, 'TextLayer')
    # add_text_to_location(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", 3*pi/4, 100, params, msp, 'TextLayer')
    # add_text_to_location(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", 5*pi/4, 100, params, msp, 'TextLayer')
    # add_text_to_location(point, "Hello PillarPlus!\nAnother Line of\nText\nAnother line\nyet another.", -pi/4, 100, params, msp, 'TextLayer')


# Saving the file:
try:
    dwg.saveas(output_file_path + output_file)
    print(f'Success in saving file: {output_file_path + output_file}')
except Exception as e:
    print(f'Failed to save the file due to the following exception: {e}')
    sys.exit(1)