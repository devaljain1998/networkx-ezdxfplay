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

def add_text_to_chamber(msp, entity, params, **args):
    """This function adds text to a chamber.
    Params is really useful here as it will be consisting of the outer boundries.

    Args:
        entity ([type]): [description]
        params (dict): The params dict of PillarPlus.
    """
    # print(f'Inside text to function: {entity}')
    
    # Get conversion factor:
    if len(args) > 0: layer_name = args['layer_name']
    conversion_factor = params['Units conversion factor']

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
    
    # Types of chambers:
    # gully trap chamber
    # inspection chamber
    # rainwater chamber
    if entity['type'] == 'gully trap chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 30 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 50 * conversion_factor
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
        DEPTH: {entity['depth']}
        GULLY TRAP
        CHAMBER
        SIZE: {size}
        """
        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 1 * conversion_factor
        
        point = list(straight_line_point)
        
        # Declaring Variable boundry_vertex points:
        x_extra_distance = (12 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-10 * conversion_factor)
        y_extra_height = (6 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (6 * conversion_factor)
        y_lower_height = -5
        
        # Build a box boundry:
        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': 'TextLayerBoundry'})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-11 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (7 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (7 * conversion_factor)

        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])
        # Setting border for the text:
        # mtext = mtext.set_bg_color(2, scale = 1.5)
        # mtext.dxf.box_fill_scale = 5
        print('dxf.bg_fill', mtext.dxf.bg_fill)
        print('Box Fill Scale: ', mtext.dxf.box_fill_scale)
        
        print('width', mtext.dxf.width)

    elif entity['type'] == 'inspection chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 30 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 50 * conversion_factor
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
        DEPTH: {entity['depth']}
        INSPECTION
        CHAMBER
        SIZE: {size}
        """
        
        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 1 * conversion_factor
        
        point = list(straight_line_point)
        
        # Declaring Variable boundry_vertex points:
        x_extra_distance = (12 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-10 * conversion_factor)
        y_extra_height = (6 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (6 * conversion_factor)
        y_lower_height = -5
        
        # Build a box boundry:
        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': 'TextLayerBoundry'})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-11 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (7 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (7 * conversion_factor)

        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])
        # Setting border for the text:
        # mtext = mtext.set_bg_color(2, scale = 1.5)
        # mtext.dxf.box_fill_scale = 5
        print('dxf.bg_fill', mtext.dxf.bg_fill)
        print('Box Fill Scale: ', mtext.dxf.box_fill_scale)
        
        print('width', mtext.dxf.width)

    elif entity['type'] == 'rainwater chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 30 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 50 * conversion_factor
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
        DEPTH: {entity['depth']}
        RAIN WATER
        CHAMBER
        SIZE: {size}
        """

        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 1 * conversion_factor
        
        point = list(straight_line_point)
        
        # Declaring Variable boundry_vertex points:
        x_extra_distance = (12 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-10 * conversion_factor)
        y_extra_height = (6 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (6 * conversion_factor)
        y_lower_height = -5
        
        # Build a box boundry:
        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': 'TextLayerBoundry'})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-11 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (7 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (7 * conversion_factor)

        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])
        # Setting border for the text:
        # mtext = mtext.set_bg_color(2, scale = 1.5)
        # mtext.dxf.box_fill_scale = 5
        print('dxf.bg_fill', mtext.dxf.bg_fill)
        print('Box Fill Scale: ', mtext.dxf.box_fill_scale)
        
        print('width', mtext.dxf.width)

    else:
        raise ValueError(
            'Only chambers with types: ("gully trap chamber", "inspection chamber", "rainwater chamber") are allowed.')    
    
    print(
        f'Successfully added slant_line: {slant_line} and straight_line: {straight_line}\n\n')


if __name__ == '__main__':
    import csv

    this_dir = os.path.dirname(__file__)

    if this_dir != '':
        this_dir += '/'

    # Read parameters.csv (Generally common for most projects)
    try:
        params_dict = {}
        with open(this_dir + 'parameters.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    # print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    value = row[1].strip()
                    # print(f'{row[0]} is {value}')
                    if value.isnumeric():
                        value = float(value)
                    elif value.lower() == 'yes':
                        value = True
                    elif value.lower() == 'no':
                        value = False
                    params_dict[row[0].strip()] = value
                    line_count += 1
            # print(f'Processed {line_count} lines.')
    except FileNotFoundError:
        print(f'Parameters file "parameters.csv" is missing')
        exit()


    # FILE READING
    autocad_file = this_dir + params_dict['ProjectFolder'] + 'updated_in.dxf'
    dwg = ezdxf.readfile(autocad_file)
    msp = dwg.modelspace()

    with open(this_dir + params_dict['ProjectFolder'] + 'updated_identification.json') as json_file:
        identification_json = json.load(json_file)


    # Testing chambers:
    entities = identification_json['entities']
    params = identification_json["params"]
    conversion_factor = params['Units conversion factor']
    # Calling function by hardcoding:
    for entity in entities:
        if 'chamber' in entity['type']:
            add_text_to_chamber(msp,entity, params)


    # Saving the file:
    try:
        dwg.saveas(this_dir + params_dict['ProjectFolder'] + 'texting output.dxf')
        print(f'Success in saving file:' + this_dir + params_dict['ProjectFolder'] +' drainage output.dxf')
    except Exception as e:
        print(f'Failed to save the file due to the following exception: {e}')
        sys.exit(1)