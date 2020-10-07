import json
import math
import os
import pprint
import sys
from math import *

import ezdxf
from ezdxf.math import Vec2, Vector

from pillarplus.math import (directed_points_on_line, find_distance,
                             find_perpendicular_point,
                             get_angle_between_two_points,
                             get_distance_of_point_to_a_line)

file_path = 'Algorithms/MText/input/'
input_file = 'chamber_test.dxf'
output_file_path = 'Algorithms/MText/output/'
input_file_name = input_file.split('.')[0]
output_file = 'output_chamber_WALL_TEST.dxf'

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



def add_text_on_wall(point: tuple, text: str, wall, conversion_factor: float):
    """This function adds text on the wall.

    Args:
        point (tuple): A list of point.
        text (str): The which is needed to be added.
        wall (entity): Wall is an entity.
    """
    # Get corners of the wall
    corners = wall['corners']
    
    # Check the point is closed to which corner
    closest_corner = corners[0] if find_distance(point, corners[0]) <= find_distance(point, corners[1]) else corners[1]

    # Get the in-angle and get opposite angle for it.
    in_angle = wall['in_angle']
    opposite_in_angle = in_angle + 180
    
    # find distance of point to wall:
    distance = ezdxf.math.distance_point_line_2d(Vec2(point), Vec2(corners[0]), Vec2(corners[1]))
    
    # Move find the point above x distance with closest corner:
    #(.) -> The point can be here. That is why we are finding a parallel distance.
    # .
    # _________
    point_above_closest_corner = directed_points_on_line(closest_corner, pi/2, distance)[0]
    
    # Forming a vector with point and point_above_closest_corner
    vector = Vector(point_above_closest_corner[0] - point[0], point_above_closest_corner[1] - point[1])
    angle = vector.angle_deg
    
    # In degree
    angle_for_slant_line = (angle + opposite_in_angle) / 2

    # Draw in line in the direction of angle:
    slant_line_length = 300 * conversion_factor
    slant_line = directed_points_on_line(
        point, math.radians(angle_for_slant_line), slant_line_length)
    msp.add_line(point, slant_line[0], dxfattribs={
                 'layer': 'TextLayer'})

    # Drawing straight line:
    straight_line_length = 500 * conversion_factor
    angle: float = vector.angle
    straight_line = directed_points_on_line(
        slant_line[0], angle, straight_line_length)
    msp.add_line(slant_line[0], straight_line[0],
                 dxfattribs={'layer': 'TextLayer'})
    
    mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
    mtext.dxf.char_height = 10 * conversion_factor
    
    point = list(straight_line[0])
    # Increasing the Y coordinate for proper positioning
    # point[0] -= (10 * conversion_factor)
    # point[0] += 270
    # point[1] += (60 * conversion_factor)
    mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])    
    mtext.set_rotation(vector.angle_deg)
    
    print(f'Success in adding mtext at the location: {point} and angle: {opposite_in_angle}.')
    
    try:
        dwg.saveas(output_file_path + output_file)
        print(f'Successfully saved the file at: {output_file_path + output_file}')
    except Exception as e:
        print(f'Failed to save the file due to the following exception: {e}')
        sys.exit(1)



# Testing add text to wall:
walls = identification_json['walls']
switch_boards = [i for i in range(12, 24)]
entities = identification_json['entities']
params = identification_json["params"]
conversion_factor = params['Units conversion factor']

# Calling function by hardcoding:
for i in switch_boards:
    switch_board = entities[i]
    wall = list(filter(lambda wall: wall['number'] == switch_board['wall_number'], walls))[0]
    point = switch_board['location']
    add_text_on_wall(point, "Hello PillarPlus!\nAnother Line of\nText.", wall, conversion_factor)
