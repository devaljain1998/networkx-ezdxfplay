import sys
import ezdxf
import os
import pprint
import math
import ezdxf
import json
from ezdxf.math import Vector
from pillarplus.math import find_distance, get_angle_between_two_points, directed_points_on_line


file_path = 'Algorithms/MText/input/'
input_file = 'chamber.dxf'
output_file_path = 'Algorithms/MText/output/'
input_file_name = input_file.split('.')[0]
output_file = 'chamber_mtext.dxf'

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
json_file_path = 'Algorithms/MText/identification.json'
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




def add_text_to_chamber(entity, params):
    """This function adds text to a chamber.
    Params is really useful here as it will be consisting of the outer boundries.

    Args:
        entity ([type]): [description]
        params (dict): The params dict of PillarPlus.
    """
    print(f'Inside text to function: {entity}')
    # Get the centre point of the chamber
    centre_point = entity["location"]

    # Find in which direction we need to draw the line from the outer
    # 1. Get the 4 corners:
    min_x, min_y = params["PP-OUTER minx"], params["PP-OUTER miny"]
    max_x, max_y = params["PP-OUTER maxx"], params["PP-OUTER maxy"]

    # 2. Now find the direction by check where is the centre-point closest
    if find_distance((min_x, 0), (centre_point[0], 0)) <= find_distance((centre_point[0], 0), (max_x, 0)):
        dir_x = min_x
    else:
        dir_x = max_x

    if find_distance((0, min_y), (0, centre_point[1])) <= find_distance((0, centre_point[1]), (0, max_y)):
        dir_y = min_y
    else:
        dir_y = max_y

    # Stretch distance in the direction of x and y:
    angle: float = get_angle_between_two_points(
        (dir_x, 0, 0), (0, dir_y, 0)) / 2

    # Draw in line in the direction of angle:
    slant_line_length = 300
    slant_line = directed_points_on_line(
        centre_point, angle, slant_line_length)
    msp.add_line(centre_point, slant_line[0], dxfattribs={
                 'layer': 'TextLayer'})

    # Drawing straight line:
    straight_line_length = 500
    angle: float = 0
    straight_line = directed_points_on_line(
        slant_line[0], angle, straight_line_length)
    msp.add_line(slant_line[0], straight_line[0],
                 dxfattribs={'layer': 'TextLayer'})

    # Types of chambers:
    # gully trap chamber
    # inspection chamber
    # rainwater chamber
    if entity['type'] == 'gully trap chamber':
        size = '1\'.0"X1\'0"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity['chamber_depth']}
        {entity['type'].upper()}
        SIZE: {size}
        """
        # MTEXT Formatting
        mtext = msp.add_mtext("", dxfattribs={'layer': 'TextLayer'})
        mtext += text
        mtext.dxf.char_height = 50
        
        point = list(straight_line[0])
        # Increasing the Y coordinate for proper positioning
        point[1] += 300
        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])
        # Setting border for the text:
        #mtext.dxf.box_fill_scale = 5
        print('Box Fill Scale: ', mtext.dxf.box_fill_scale)
        
        print('width', mtext.dxf.width)

    elif entity['type'] == 'inspection chamber':
        size = '1\'.6"X1\'6"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity['chamber_depth']}
        {entity['type'].upper()}
        SIZE: {size}
        """

        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.set_location(straight_line[1])

    elif entity['type'] == 'rainwater chamber':
        size = '1\'.0"X1\'0"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity['chamber_depth']}
        {entity['type'].upper()}
        SIZE: {size}
        """

        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.set_location(straight_line[1])

    else:
        raise ValueError(
            'Only chambers with types: ("gully trap chamber", "inspection chamber", "rainwater chamber") are allowed.')    
        
    # Saving the file:
    try:
        dwg.saveas(output_file_path + output_file)
    except Exception as e:
        print(f'Failed to save the file due to the following exception: {e}')
        sys.exit(1)
    print(
        f'Successfully added slant_line: {slant_line} and straight_line: {straight_line}')
