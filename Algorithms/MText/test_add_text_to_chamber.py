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

file_path = 'Algorithms/MText/input/'
input_file = 'chamber_test.dxf'
output_file_path = 'Algorithms/MText/output/'
input_file_name = input_file.split('.')[0]
output_file = 'output_chamber_TEST.dxf'

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

msp = dwg.modelspace()
print(f'DXF File read success from {file_path}.')

# Reading the identification JSON:
json_file_path = 'Algorithms/MText/chamber_identification.json'
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

def convert_point_to_inch(point):
    mm_point = point[0] * 0.0393701, point [1] * 0.0393701
    print(f'point: {point}, mm: {mm_point}')


def add_text_to_chamber(entity, params, *args):
    """This function adds text to a chamber.
    Params is really useful here as it will be consisting of the outer boundries.

    Args:
        entity ([type]): [description]
        params (dict): The params dict of PillarPlus.
    """
    # print(f'Inside text to function: {entity}')
    
    # Get conversion factor:
    if len(args) > 0: conversion_factor = args[0]
    
    # Get the centre point of the chamber
    centre_point = entity["location"]

    # Find in which direction we need to draw the line from the outer
    # 1. Get the 4 corners:
    min_x, min_y = params["PP-OUTER minx"], params["PP-OUTER miny"]
    max_x, max_y = params["PP-OUTER maxx"], params["PP-OUTER maxy"]
    
    print(f'min_min x,y', (min_x, min_y))
    print(f'max_max x,y', (max_x, max_y))
    print('CentrePoint: ', centre_point)

    # 2. Now find the direction by check where is the centre-point closest
    def get_direction(min_x, min_y, max_x, max_y, centre_point):
        if find_distance((min_x, 0), (centre_point[0], 0)) <= find_distance((centre_point[0], 0), (max_x, 0)):
            print('Chosen min_x', min_x)
            dir_x = min_x
        else:
            print('Chosen max_x', max_x)
            dir_x = max_x

        if find_distance((0, min_y), (0, centre_point[1])) <= find_distance((0, centre_point[1]), (0, max_y)):
            print('Chosen min_y', min_y)
            dir_y = min_y
        else:
            print('Chosen max_y', max_y)
            dir_y = max_y
            
        return dir_x, dir_y
    
    dir_x, dir_y = get_direction(min_x, min_y, max_x, max_y, centre_point)
        
    def get_slant_line_angle(dir_x, dir_y, centre_point):
        # Create Vectors
        centre_point_vector = Vector(centre_point)
        # Y coordinate will be 0
        x_dir_coordinates = (dir_x - centre_point_vector.x, 0) #x_dir_vector = Vector() - centre_point_vector
        # X coordinate will be 0
        y_dir_coordinates = (0, dir_y - centre_point_vector.y)
        print({'centre_point_vector': centre_point_vector, 'x_dir_coordinates': x_dir_coordinates, 'y_dir_coordinates': y_dir_coordinates})
        # print('p1', (dir_x - centre_point[0], 0), '\np2',(0, dir_y - centre_point[1]))
        #angle: float = get_angle_between_two_points((dir_x - centre_point[0], -centre_point[1]), (-centre_point[0], dir_y - centre_point[1]), centre_point) / 2
        angle: float = get_angle_between_two_points(x_dir_coordinates, y_dir_coordinates)
        print('angle after choosing dir for slant line: ', angle, math.degrees(angle))
        return angle
        
    slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
    # Draw in line in the direction of angle:
    slant_line_length = 300 * conversion_factor
    slant_line = directed_points_on_line(
        centre_point, slant_line_angle, slant_line_length)
    msp.add_line(centre_point, slant_line[0], dxfattribs={
                 'layer': 'TextLayer'})

    # Drawing straight line:
    straight_line_length = 500 * conversion_factor
    angle: float = 0
    straight_line = directed_points_on_line(
        slant_line[0], angle, straight_line_length)
    
    # Find which point (0 or 1) of straight line should be used:
    straight_line_point = straight_line[0] if 0 <= abs(
        degrees(slant_line_angle)) <= 90 else straight_line[1]
    
    msp.add_line(slant_line[0], straight_line_point,
                 dxfattribs={'layer': 'TextLayer'})

    # Types of chambers:
    # gully trap chamber
    # inspection chamber
    # rainwater chamber
    if entity['type'] == 'gully trap chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 300 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 500 * conversion_factor
        angle: float = 0
        straight_line = directed_points_on_line(
            slant_line[0], angle, straight_line_length)
        
        # Find which point (0 or 1) of straight line should be used:
        straight_line_point = straight_line[0] if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else straight_line[1]
        
        msp.add_line(slant_line[0], straight_line_point,
                    dxfattribs={'layer': 'TextLayer'})
        
        size = '1\'.0"X1\'0"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity['chamber_depth']}
        GULLY TRAP
        CHAMBER
        SIZE: {size}
        """
        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 10 * conversion_factor
        
        point = list(straight_line_point)
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-100 * conversion_factor)
        # Increasing the Y coordinate
        point[1] += (100 * conversion_factor)
        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])
        # Setting border for the text:
        mtext = mtext.set_bg_color(2, scale = 1.5)
        mtext.dxf.box_fill_scale = 5
        
        print('dxf.bg_fill', mtext.dxf.bg_fill)
        print('Box Fill Scale: ', mtext.dxf.box_fill_scale)
        
        print('width', mtext.dxf.width)

    elif entity['type'] == 'inspection chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 300 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 500 * conversion_factor
        angle: float = 0
        straight_line = directed_points_on_line(
            slant_line[0], angle, straight_line_length)
        
        # Find which point (0 or 1) of straight line should be used:
        straight_line_point = straight_line[0] if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else straight_line[1]
        
        msp.add_line(slant_line[0], straight_line_point,
                    dxfattribs={'layer': 'TextLayer'})
                
        size = '1\'.6"X1\'6"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity['chamber_depth']}
        INSPECTION
        CHAMBER
        SIZE: {size}
        """
        
        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 10 * conversion_factor
        
        point = list(straight_line_point)
        # Increasing the Y coordinate for proper positioning
        point[1] += (100 * conversion_factor)
        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])        

    elif entity['type'] == 'rainwater chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 300 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 500 * conversion_factor
        angle: float = 0
        straight_line = directed_points_on_line(
            slant_line[0], angle, straight_line_length)
        
        # Find which point (0 or 1) of straight line should be used:
        straight_line_point = straight_line[0] if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else straight_line[1]
        
        msp.add_line(slant_line[0], straight_line_point,
                    dxfattribs={'layer': 'TextLayer'})
        
        size = '1\'.0"X1\'0"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity['chamber_depth']}
        RAIN WATER
        CHAMBER
        SIZE: {size}
        """

        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 10 * conversion_factor
        
        point = list(straight_line_point)
        # Increasing the Y coordinate for proper positioning
        point[1] += (100 * conversion_factor)
        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])        

    else:
        raise ValueError(
            'Only chambers with types: ("gully trap chamber", "inspection chamber", "rainwater chamber") are allowed.')    
    
    print(
        f'Successfully added slant_line: {slant_line} and straight_line: {straight_line}\n\n')

# Testing gully trap chambers:
gully_trap_chambers_entities = [0, 3, 6, 9, 2, 5, 8, 11, 1, 4, 7, 10]
entities = identification_json['entities']
params = identification_json["params"]
conversion_factor = params['Units conversion factor']
# Calling function by hardcoding:
for i in gully_trap_chambers_entities:
    add_text_to_chamber(entities[i], params, conversion_factor)


# Saving the file:
try:
    dwg.saveas(output_file_path + output_file)
    print(f'Success in saving file: {output_file_path + output_file}')
except Exception as e:
    print(f'Failed to save the file due to the following exception: {e}')
    sys.exit(1)