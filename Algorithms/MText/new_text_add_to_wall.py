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

file_path = 'Algorithms/MText/input/mm file/'
input_file = 'in.dxf'
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
json_file_path = 'Algorithms/MText/mm_identification.json'
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
    if in_angle < 0: in_angle = 360 + in_angle
    
    # Opposite in_angle:
    opposite_in_angle = (in_angle + 180) % 360
    
    # find distance of point to wall:
    distance = ezdxf.math.distance_point_line_2d(Vec2(point), Vec2(corners[0]), Vec2(corners[1]))
    
    # Move find the point above x distance with closest corner:
    #(.) -> The point can be here. That is why we are finding a parallel distance.
    # .
    # _________
    point_above_closest_corner = directed_points_on_line(closest_corner, radians(in_angle), distance)[0]
    
    # Forming a vector with point and point_above_closest_corner
    vector = Vector(point_above_closest_corner[0] - point[0], point_above_closest_corner[1] - point[1])
    angle = vector.angle_deg
    if angle < 0: angle = 360 + angle
    
    # Creating vector from opposite_in_angle and point:
    opposite_point = directed_points_on_line(point, radians(opposite_in_angle), vector.magnitude)[0]
    opposite_vector = Vec2(opposite_point[0] - point[0], opposite_point[1] - point[1])
    
    angle_between_both_vectors = (vector + opposite_vector).angle_deg
    if angle_between_both_vectors < 0: angle_between_both_vectors = 360 + angle_between_both_vectors
    
    # Draw slant line:
    slant_line_length = 15 * conversion_factor
    slant_line = directed_points_on_line(
        point, math.radians(angle_between_both_vectors), slant_line_length)
    msp.add_line(point, slant_line[0], dxfattribs={
                 'layer': 'TextLayer'})
    print(f'Drawing slant_line of length: {slant_line_length} at point: {point}, sl: {slant_line}')    
    
    # Drawing straight line:
    def get_straight_line_length(text) -> float:
        """This function returns the length of the largest line in the text.
        """
        straight_line_length = 0
        lines = text.split('\n')
        for line in lines: straight_line_length = max(straight_line_length, len(line))
        return straight_line_length
        
    # straight_line_length = 25 * conversion_factor
    straight_line_length = get_straight_line_length(text) * conversion_factor
    
    straight_line_angle: float = 0 #if 0 <= abs(angle_for_slant_line) <= 90 else pi
    straight_line = directed_points_on_line(
        slant_line[0], straight_line_angle, straight_line_length)

    # Find straight line point according to slant line angle quadrant
    # 1st and 4th quadrant
    if (0 <= angle_between_both_vectors <= 90) or (270 <= angle_between_both_vectors < 360):
        straight_line_point = straight_line[0]
    else:
        straight_line_point = straight_line[1]

    # Draw straight line:
    msp.add_line(slant_line[0], straight_line_point, dxfattribs={
                 'layer': 'TextLayer'})
        
    # Mtext operations
    mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
    
    # Positioning mtext:
    mtext_x_shift = 10 * conversion_factor
    mtext_y_shift = 12 * conversion_factor
    
    if 0 <= angle_between_both_vectors < 90:
        mtext_x_coordinate = straight_line_point[0] - mtext_x_shift
    elif 90 <= angle_between_both_vectors < 180:
        mtext_x_coordinate = straight_line_point[0] + mtext_x_shift
    elif 180 <= angle_between_both_vectors < 270:
        mtext_x_coordinate = straight_line_point[0] + mtext_x_shift
    elif 270 <= angle_between_both_vectors < 360:
        mtext_x_coordinate = straight_line_point[0] - mtext_x_shift
    else:
        raise ValueError(f'angle_between_both_vectors should be between 0 to 360 degrees. Got: {angle_between_both_vectors}.')
    
    if 0 <= angle_between_both_vectors <= 180:
        mtext_y_coordinate = straight_line_point[1] + mtext_y_shift
    else:
        mtext_y_coordinate = straight_line_point[1] + mtext_y_shift
        
    mtext_point = (mtext_x_coordinate, mtext_y_coordinate)
    
    mtext.set_location(mtext_point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"]) 
    
    print(f'Success in adding mtext at the point: {point} for wall: {wall["number"]}.\n')
    
    try:
        dwg.saveas(output_file_path + output_file)
        print(f'Successfully saved the file at: {output_file_path + output_file}')
    except Exception as e:
        print(f'Failed to save the file due to the following exception: {e}')
        sys.exit(1)




# Testing add text to wall:
walls = identification_json['walls']
switch_boards = [i for i in range(12, 24)] #24
entities = identification_json['entities']
params = identification_json["params"]
conversion_factor = params['Units conversion factor']

# Calling function by hardcoding:
for i in switch_boards:
    switch_board = entities[i]
    wall = list(filter(lambda wall: wall['number'] == switch_board['wall_number'], walls))[0]
    point = switch_board['location']
    print(f'Point: {point}')
    add_text_on_wall(point, "Hello PillarPlus!\nAnother Line of\nText.", wall, 1.0)