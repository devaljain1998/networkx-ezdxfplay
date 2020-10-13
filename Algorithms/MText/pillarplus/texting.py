import sys
import ezdxf
import os
import pprint
import math
import ezdxf
import json
from ezdxf.math import Vector
from math import *

from .math import find_distance, get_angle_between_two_points, directed_points_on_line, find_mid_point

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

def get_cleaned_text(text: str):
    """This function cleans text.

    Args:
        text (str): [description]

    Returns:
        [type]: [description]
    """
    text = text.replace('/', '\n')
    text = text.replace('$', '\n')
    return text

def find_text_rotation(p1,p2):
    '''
    find the angle for text to rotate
    Parameters: takes two points (location) (list or tuple)
    Return: angle in degrees
    Dependencies: find_rotation function in pillarplus.math
    '''
    rotation = math.find_rotation(p1,p2)
    if (abs(rotation)>90):
        rotation += 180
    return rotation


# def __add_text_to_pipe(connection, source, target, distance, _msp, pipe_length, conversion_factor):
#     pipe_text = connection['text']
#     pipe_text_location = math.find_directed_point(source['location'],target['location'],distance/2)
#     if pipe_text != None:
#         if pipe_text != '//':
#             pipe_rotation = find_text_rotation(start_connection,end_connection)
#             leader_flag = 0
#             #add leader if required
#             if pipe_length < 500 * conversion_factor:                                               #--:warning:-- (HCV)
#                 #draw ledger and add text 
#                 angle = 135                                                                         #--:warning:-- (HCV)
#                 dist = 200 * conversion_factor                                                      #--:warning:-- (HCV)
#                 pipe_text_location = draw_leader(pipe_text_location,angle,dist)
#                 leader_flag = 1
#             # adding text
#             if leader_flag:
#                 pipe_rotation = 0
#             _msp.add_text(pipe_text,
#                             dxfattribs={'height': TEXT_HEIGHT, 'layer':layer_name, 'rotation':pipe_rotation}).set_pos(
#                                 pipe_text_location,align='MIDDLE_CENTER')               # --:warning:-- (hcv - text height)
#     else:
#         print("pipe text is None for connection no. "+ str(connection['number']))


# TEXTING FUNCTIONS:
# 1. ADD TEXT TO CONNECTION
def add_text_to_connection(connection, connection_start, connection_end, params: dict, msp, layer_name: str = None) -> None:
    if connection_start is None or connection_end is None:
        raise ValueError(f"Exception: connection_start and connection_end can never be null: {connection}")
    
    # Cleaning text:
    text = connection['text']
    text = get_cleaned_text(text)
    
    # Get conversion factor:
    conversion_factor: float = params['Units conversion factor']
    
    # Defining constant for minimum connection length:
    MINIMUM_CONNECTION_SIZE = 100 * conversion_factor
    CONNECTION_TEXT_EXTRA_HEIGHT = 100 * conversion_factor
    
    # Fetching text from connection:
    text = connection['text']
    
    # Handling cases of desired texting sizes
    if connection['size'] >= MINIMUM_CONNECTION_SIZE:
        # Find midpoint of the connection:
        mid_point = find_mid_point(connection_start, connection_end)
        
        # finding angle on which the text is to be placed:
        slant_line_angle = (find_text_rotation(connection_start, connection_end) + 90) % 360
        
        # place slant line:
        slant_line_length = 500 * conversion_factor
        slant_line = directed_points_on_line(mid_point, radians(slant_line_angle), slant_line_length)[0]
        msp.add_line(slant_line[0], slant_line[1], dxfattribs = {'layer': layer_name})
        
        # Place straight line:
        def get_straight_line_length(text) -> float:
            """This function returns the length of the largest line in the text.
            """
            straight_line_length = 0
            lines = text.split('\n')
            for line in lines: straight_line_length = max(straight_line_length, len(line))
            STRAIGHT_LINE_SCALE_FACTOR = 10
            return (straight_line_length * STRAIGHT_LINE_SCALE_FACTOR) * conversion_factor
        
        straight_line_length = get_straight_line_length()
        straight_line_angle = 0
        straight_line = directed_points_on_line(slant_line[1], radians(straight_line_angle), straight_line_length)
        is_x_increasing = connection_end[0] - connection_start[0] >= 0
        
        straight_line_point = straight_line[0] if is_x_increasing else straight_line[1]
        msp.add_line(slant_line[1], straight_line_point, dxfattribs = {'layer': layer_name})
        
        
        # Now placing MText:
        mtext = msp.add_mtext(connection['text'], dxfattribs={'layer': layer_name})
        
        # Positioning mtext:
        mtext_x_shift = 50 * conversion_factor
        mtext_y_shift = 60 * conversion_factor
        
        # Cleaning slant_line_angle
        if slant_line_angle < 0: slant_line_angle += 360
        elif slant_line_angle >= 360: slant_line_angle %= 360

        if 0 <= slant_line_angle < 90:
            mtext_x_coordinate = straight_line_point[0] - mtext_x_shift
        elif 90 <= slant_line_angle < 180:
            mtext_x_coordinate = straight_line_point[0] + mtext_x_shift
        elif 180 <= slant_line_angle < 270:
            mtext_x_coordinate = straight_line_point[0] + mtext_x_shift
        elif 270 <= slant_line_angle < 360:
            mtext_x_coordinate = straight_line_point[0] - mtext_x_shift
        else:
            raise ValueError(f'slant_line_angle should be between 0 to 360 degrees. Got: {slant_line_angle}.')
        
        if 0 <= slant_line_angle <= 180:
            mtext_y_coordinate = straight_line_point[1] + mtext_y_shift
        else:
            mtext_y_coordinate = straight_line_point[1] + mtext_y_shift
        
        mtext_point = (mtext_x_coordinate, mtext_y_coordinate)
        mtext.set_location(mtext_point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"]) 
        
        print(f'Success in adding mtext at the point: {mtext_point} for connection: {connection}.\n')
        
    
    # Handling case of texting when the connection size is very less
    else:
        pass

# 2. ADD TEXT TO CHAMBER
def add_text_to_chamber(msp, entity, params: dict, layer_name: str = None, **args):
    """This function adds text to a chamber.
    Params is really useful here as it will be consisting of the outer boundries.

    Args:
        entity ([type]): [description]
        params (dict): The params dict of PillarPlus.
    """
    # print(f'Inside text to function: {entity}')
    
    # Get conversion factor:
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
        slant_line_length = 1500 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 250 * conversion_factor
        angle: float = 0
        straight_line = directed_points_on_line(
            slant_line[0], angle, straight_line_length)
        
        # Find which point (0 or 1) of straight line should be used:
        straight_line_point = straight_line[0] if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else straight_line[1]
        
        msp.add_line(slant_line[0], straight_line_point,
                    dxfattribs={'layer': layer_name})
        
        size = '1\'.0"X1\'0"'

        text = f"""
        F.GL: {entity['finish_floor_level']}
        I.LVL: {entity['invert_level']}
        DEPTH: {entity.get('chamber_depth')}
        GULLY TRAP
        CHAMBER
        SIZE: {size}
        """
        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 60 * conversion_factor
        
        point = list(straight_line_point)
        
        # Declaring Variable boundry_vertex points:
        x_extra_distance = (720 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-600 * conversion_factor)
        y_extra_height = (360 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (360 * conversion_factor)
        y_lower_height = -300 * conversion_factor
        
        # Build a box boundry:
        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': 'TextLayerBoundry'})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-440 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (420 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (280 * conversion_factor)

        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])

    elif entity['type'] == 'inspection chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 400 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 250 * conversion_factor
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
        DEPTH: {entity.get('chamber_depth')}
        INSPECTION
        CHAMBER
        SIZE: {size}
        """
        
        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': 'TextLayer'})
        mtext.dxf.char_height = 60 * conversion_factor
        
        point = list(straight_line_point)
        
        # Declaring Variable boundry_vertex points:
        x_extra_distance = (720 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-600 * conversion_factor)
        y_extra_height = (360 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (360 * conversion_factor)
        y_lower_height = -300 * conversion_factor
        
        # Build a box boundry:
        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': layer_name})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-440 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (420 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (280 * conversion_factor)

        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])

    elif entity['type'] == 'rainwater chamber':
        slant_line_angle = get_slant_line_angle(dir_x, dir_y, centre_point)
        # Draw in line in the direction of angle:
        slant_line_length = 1800 * conversion_factor
        slant_line = directed_points_on_line(
            centre_point, slant_line_angle, slant_line_length)
        msp.add_line(centre_point, slant_line[0], dxfattribs={
                    'layer': 'TextLayer'})

        # Drawing straight line:
        straight_line_length = 250 * conversion_factor
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
        DEPTH: {entity.get('chamber_depth')}
        RAIN WATER
        CHAMBER
        SIZE: {size}
        """

        # MTEXT Formatting
        mtext = msp.add_mtext(text, dxfattribs={'layer': layer_name})
        mtext.dxf.char_height = 60 * conversion_factor
        
        point = list(straight_line_point)
        
        # Declaring Variable boundry_vertex points:
        x_extra_distance = (720 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-600 * conversion_factor)
        y_extra_height = (360 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (360 * conversion_factor)
        y_lower_height = -300 * conversion_factor
        
        # Build a box boundry:
        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': 'TextLayerBoundry'})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-440 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (420 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (280 * conversion_factor)

        mtext.set_location(point, None, MTEXT_ATTACHMENT_POINTS["MTEXT_TOP_CENTER"])

    else:
        raise ValueError(
            'Only chambers with types: ("gully trap chamber", "inspection chamber", "rainwater chamber") are allowed.')    
    
    print(
        f'Successfully added slant_line: {slant_line} and straight_line: {straight_line}\n\n')


# 3. ADD TEXT TO PIPING
def add_text_to_piping(params: dict, msp, layer_name: str = None) -> None:
    pass

# 4. ADD TEXT TO WALL
def add_text_to_wall(point: tuple, text: str, wall, params: dict, msp, layer_name: str = None) -> None:
    """This function adds text on the wall.

    Args:
        point (tuple): A list of point.
        text (str): The which is needed to be added.
        wall (entity): Wall is an entity.
    """
    # Get conversion factor:
    conversion_factor: float = params['Units conversion factor']
    
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


# 5. ADD TEXT TO LOCATION
def add_text_to_location(params: dict, msp, layer_name: str = None) -> None:
    pass