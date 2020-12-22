import math
from typing import Dict, List

from pillarplus.math import (are_lines_overlapping, find_distance,
                             find_perpendicular_point, find_slope,
                             get_distance_between_two_parallel_lines,
                             get_length_of_line_segment, get_line_points_2d,
                             get_mid_points_between_points, is_between,
                             is_line_decreasing_on_x_2d, is_polyline_closed)


class CentreLine:
    """This class represents a centerline object.
    
    Attributes:
        number: int
        start_point: point
        end_point: point
        screen_start_point: point
        screen_end_point: point
        width : float
    """
    
    def __init__(self, number: int, start_point, end_point, 
                    screen_start_point, screen_end_point, width: float):
        self.number = number
        self.start_point = start_point
        self.end_point = end_point
        self.screen_start_point = screen_end_point
        self.screen_end_point = screen_end_point
        self.width = width
        
    def __repr__(self):
        return f'CentreLine<number:{self.number}, start_point:{self.start_point}, end_point:{self.end_point}, screen_start_point:{self.screen_start_point}, screen_end_point:{self.screen_end_point}, width:{self.width}>'
    
    def __str__(self):
        return self.__repr__()
    
    def get_closest_point(self, point):
        """This function returns the closest point (either start_point or end_point) from 
        a given point."""
        distance_to_start_point = find_distance(self.start_point, point)
        distance_to_end_point = find_distance(self.end_point, point)
        return self.start_point if distance_to_start_point <= distance_to_end_point else self.end_point

#CONSTANTS:
MAXIMUM_DISTANCE_BETWEEN_CENTRE_LINES = 500 #It is needed to be decided

line_meta = {}
def get_lines(msp, dwg, layer_name) -> List[tuple]:
    """This function returns all the lines contained in the layer "PP-Centre_line"
    of the dxf file provided.

    Returns:
        List[tuple]: Returns an 'unsorted' list of lines.
    """
    lines = []
    
    def get_lines_from_polylines(msp) -> List[tuple]:
        """This function returns all the lines contained in polylines of the layer "PP-Centre_line"
        of the dxf file provided.

        Returns:
            List[tuple]: Returns an 'unsorted' list of lines.
        """
        #fetching all the polylines from the layer PP-Centre_line
        polylines = msp.query(f'LWPOLYLINE[layer=="{layer_name}"]')
            
        def is_closed(polyline):
            CLOSED = 1
            return CLOSED == polyline.dxf.flags

        #Convert polylines into lines:
        print('Converting polylines into lines.')
        lines = []
        for polyline in polylines:
            line = []
            
            for point in polyline:
                x, y = point[0], point[1]
                line.append((x, y))
                
                #if the line has two points:
                if len(line) == 2:
                    #Check if the line is decreasing or not:
                    if is_line_decreasing_on_x_2d(line):
                        #Swap the points if the line is decreasing:
                        line.reverse()
                    
                    #Append the line into lines
                    lines.append(line)
                    line_meta[str(line)] = {'polyline' : polyline}
                    
                    #clear the line
                    line = [(x, y)]
            
            # if the polyline is closed 
            if is_polyline_closed(polyline):
                #Connecting the first and last points also:
                p1 = polyline[-1]
                x1, y1 = p1[0], p1[1]
                p2 = polyline[0]
                x2, y2 = p2[0], p2[1]
                line = [(x1, y1), (x2, y2)]
                line_meta[str(line)] = {'polyline' : polyline}
                lines.append(line)
                
        
        return lines
        
    def get_lines_from_lines(msp):
        """This function returns all the lines contained in lines of the layer "PP-Centre_line"
        of the dxf file provided.

        Returns:
            List[tuple]: Returns an 'unsorted' list of lines.
        """
        lines = []
        #fetching all the lines from the layer PP-Centre_line
        Lines = msp.query(f'LINE[layer=="{layer_name}"]')
        
        for Line in Lines:
            try:
                x1, y1, z1 = Line.dxf.start
                x2, y2, z2 = Line.dxf.end
            except Exception as e:
                print(f'Exception occured while reading line: {e}')
            
            line = [(x1, y1), (x2, y2)]
            
            if is_line_decreasing_on_x_2d(line):
                #Swap the points if the line is decreasing:
                line.reverse()
                
            line_meta[str(line)] = {'polyline' : False}
            
            lines.append(line)
                    
        return lines
        
        
    polyline_lines = get_lines_from_polylines(msp)
    line_lines = get_lines_from_lines(msp)
    lines.extend(polyline_lines)
    lines.extend(line_lines)
    
    # Sorting the lines before returning
    lines.sort()
    
    return lines



def preprocess_lines(lines: List[tuple]) -> List[tuple]:
    """This function preprocesses the lines from that are directly sent as input.

    Args:
        lines (List[tuple]): The lines directly given in the input.

    Returns:
        List[tuple]: lines.
    """
    Lines = []
    for Line in lines:
        line = [Line[0], Line[1]]
        if is_line_decreasing_on_x_2d(line): line.reverse()
        line_meta[str(line)] = {'polyline': False}
        Lines.append(line)
    # Now sorting lines:
    Lines.sort()
    return Lines

def get_slope_bucket(lines: List[List[tuple]]) -> Dict[int, List[List[tuple]]]:    
    """Returns a slope bucket with key slope and values to a be all the lines lying in that slope.
    
    Args:
        lines: (List[List[tuple]]): List of lines fetched from the layer "PP-Centre_line".

    Returns:
        Dict[int, List[List[tuple]]]: Returns a slope_bucket (dict) with key slope and values to a be all the lines lying in that slope.
    """
    def get_slope(x1, y1, x2, y2): 
        try:
            slope = (float)(y2-y1)/(float)(round(x2-x1))
        except ZeroDivisionError:
            print(f'Zerodivisionerror:: Variables are: {(x1, y1), (x2, y2)}')
            return math.inf
        return slope
    
    slopes = dict()
    #Finding slopes of every line:
    for line in lines:
        p1, p2 = line[0], line[1]
        slope = get_slope(p1[0], p1[1], p2[0], p2[1])# slope = find_slope(p1, p2)
        
        #Rounding slope for 3 decimal:
        if slope != math.inf:
            slope = round(slope, 1) #slope = round(slope, ndigits = 5)
        
        # Check if the slope exists in the slope_dict
        if slope in slopes.keys():
            slopes[slope].append(line)
        else:
            slopes[slope] = [line]
    
    return slopes

def does_lines_belong_to_same_polyline(line1, line2) -> bool:
    """Function to find that the lines belong to the same polyline or not.

    Args:
        line1 (List[List[tuple]]): List of lines fetched from the layer "PP-Centre_line".
        line2 (List[List[tuple]]): List of lines fetched from the layer "PP-Centre_line".

    Returns:
        bool: Returns True is they belong to the same polyline otherwise False.
    """
    if line_meta[str(line1)]['polyline'] == False or line_meta[str(line2)]['polyline'] == False:
        return False
    return line_meta[str(line1)]['polyline'] == line_meta[str(line2)]['polyline']


def is_almost_parallel(line1: List[tuple], line2: List[tuple],permissible_angle: int = 1) -> bool:
    """This function detects if the lines are almost parallel.

    Args:
        line1 (List[tuple]): A line which is a list of tuples
        line2 (List[tuple]): A line which is a list of tuples
        permissible_angle (int, optional): Permissible angle in degrees. Defaults to 1 degree.

    Returns:
        [bool]: Returns true if the lines are almost parallel according to the permissible angle otherwise false.
    """
    permissible_angle #angle in degree at which lines are still considered parallel
    theta1 = math.atan(find_slope(line1[0],line1[1]))*180/math.pi
    theta2 = math.atan(find_slope(line2[0],line2[1]))*180/math.pi
    if theta1<0:
        theta1 = theta1 + 180
    if theta2<0:
        theta2 = theta2 + 180
    if (theta1-theta2 < permissible_angle):
        return True
    else:
        return False


parallel_line_pair_meta = {}
def get_parallel_line_pairs(slope_bucket : Dict[int, List[List[tuple]]]) -> List[List[tuple]]:
    """This function returns the pairs of parallel lines that are chosen
    
    The following factors makes a valid parallel pair:
        - Lines should be having a distance less then or equal to threshold value. (MAXIMUM_DISTANCE_BETWEEN_Centre_lineS)
        
        - Lines should have a distance in between greater than zero.
        
        - Lines should be overlapping. (are_lines_overlapping).

    Args:
        slope_bucket (Dict[int, List[List[tuple]]]): Slope bucket which pairs the lines according to the slope.

    Returns:
        List[List[tuple]]: Returns a list of lines.
    """
    parallel_line_pairs = []
    for slope, lines in slope_bucket.items():
        print(f'Looping for slope : {slope}:\n')
        
        # fetch points in pair of two and form their pairs:
        index, i = 0, 0
        while (i < len(lines)):
            index = i #  index = 2 * i
            line1 = lines[index]
            print(f'Now making pairs for line1: {line1}:-')
            
            def _get_line2(index, counter):
                return lines[index + counter] if (index + counter < len(lines)) else None
            
            counter = 1
            line2 = _get_line2(index, counter)
            
            # Looping to form the maximum possible pairs with line1.
            while (line2):
                distance = get_distance_between_two_parallel_lines(line1, line2)
                print(f'Dist: {distance} for {line1, line2}')
                
                #edge cases:
                # Lines should not fall into each other
                if round(distance) == 0: 
                    print('REJECTED: round(distance) == 0')
                    counter += 1
                    line2 = _get_line2(index, counter)
                    continue
                
                # Lines should be overlapping
                if not are_lines_overlapping(line1, line2, slope):
                    print('REJECTED: not are_lines_overlapping(line1, line2, slope)')
                    counter += 1
                    line2 = _get_line2(index, counter)
                    continue                
                
                # Lines should be inside a threshold
                if distance > MAXIMUM_DISTANCE_BETWEEN_CENTRE_LINES: 
                    print('REJECTED: distance > MAXIMUM_DISTANCE_BETWEEN_CENTRE_LINES')
                    # break            
                    counter += 1
                    line2 = _get_line2(index, counter)
                    continue                
                
                if does_lines_belong_to_same_polyline(line1, line2):
                    print('REJECTED: does_lines_belong_to_same_polyline(line1, line2)')
                    counter += 1
                    line2 = _get_line2(index, counter)
                    continue                                

                if not is_almost_parallel(line1, line2):
                    print('REJECTED: is_almost_parallel(line1, line2)')
                    counter += 1
                    line2 = _get_line2(index, counter)
                    continue                                
                
                print(f'Forming a pair b/w {line1, line2}, slope: {slope}\n')
                #Make pair of these lines
                parallel_line_pairs.append((line1, line2))
                
                # Storing the width
                parallel_line_pair_meta[str((line1, line2))] = distance
                
                counter += 1
                line2 = _get_line2(index, counter)
                
            i +=1
            
    
    return parallel_line_pairs
    


def get_centre_lines_from_pairs(parallel_line_pairs : List[List[tuple]]) -> List["CentreLine"]:
    """This function returns the CentreLine objects that are needed.

    Args:
        parallel_line_pairs (List[List[tuple]]): These are the valid pairs of parallel lines between which a CentreLine can be constructed.

    Returns:
        List[CentreLine]: A list of CentreLine objects for the 
    """
    def get_centered_line_segments(line1, line2) -> list:
        """Function which returns a centered line segments from parallel pairs.

        Args:
            line1 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
            line2 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
            
        Returns:
            line (List of Tuples): A linesegment in middle of line1 and line2.
        """
        # Calculate lenght of both the line segment.
        line1_length = get_length_of_line_segment(line1)
        line2_length = get_length_of_line_segment(line2)
        
        smaller_line = line1 if line1_length <= line2_length else line2
        bigger_line = line1 if smaller_line == line2 else line2
        
        # We need to get perpendicular points from the smaller line to the bigger line
        p1 = smaller_line[0]
        perpendicular_point1 = find_perpendicular_point(p1, bigger_line[0], bigger_line[1])
        
        # Check if the perpendicular point exists on the other line or not:
        if is_between(perpendicular_point1, bigger_line[0], bigger_line[1]):
            # Find centre point in this case
            centre_point1 = get_mid_points_between_points(p1, perpendicular_point1)
        else:
            # we need to get the point from the bigger line now
            for point in bigger_line:
                perpendicular_point1 = find_perpendicular_point(point, smaller_line[0], smaller_line[1])
                # if this perpendicular point lies in the smaller line then break
                if is_between(perpendicular_point1, smaller_line[0], smaller_line[1]):
                    # calculate the centre point first
                    centre_point1 = get_mid_points_between_points(point, perpendicular_point1)                
                    break
                    
        # We need to get perpendicular points from the smaller line to the bigger line
        p2 = smaller_line[1]
        perpendicular_point2 = find_perpendicular_point(p2, bigger_line[0], bigger_line[1])
        
        # Check if the perpendicular point exists on the other line or not:
        if is_between(perpendicular_point2, bigger_line[0], bigger_line[1]):
            # Find centre point in this case
            centre_point2 = get_mid_points_between_points(p2, perpendicular_point2)
        else:
            # we need to get the point from the bigger line now
            for point in bigger_line:
                perpendicular_point2 = find_perpendicular_point(point, smaller_line[0], smaller_line[1])
                # if this perpendicular point lies in the smaller line then break
                if is_between(perpendicular_point2, smaller_line[0], smaller_line[1]):
                    # calculate the centre point first
                    centre_point2 = get_mid_points_between_points(point, perpendicular_point2)
                    break
                
        return [centre_point1, centre_point2]
    
    
    centre_lines = []
    number = 1
    for pair in parallel_line_pairs:
        line1, line2 = pair
        
        if line2:
            x1, y1, x2, y2 = get_line_points_2d(line1)
                            
            print(f'Now calculating line segment {line1, line2}')                
            
            line_segment = get_centered_line_segments(line1, line2)
            
            print(f"""
                line1: {line1},
                line2: {line2},
                line_segment: {line_segment}\n\n
                """)
            
            width = parallel_line_pair_meta[str(pair)]
            if find_distance(line_segment[0], line_segment[1]) >= 5:
                    centre_line = CentreLine(number, line_segment[0], line_segment[1], line_segment[0], line_segment[1], width)
                    
                    centre_lines.append(centre_line)
                    
                    number += 1
            
    return centre_lines


def draw_Centre_lines(Centre_lines, msp, dwg, output_file):
    def __debug_location(point, name: str = 'debug', radius = 2, color:int = 2):
        msp.add_circle(point, radius, dxfattribs={'color': color, 'layer': 'debug'})
        msp.add_mtext(name, dxfattribs = {'layer': 'debug'}).set_location(point)

    for Centre_line in Centre_lines:
        msp.add_line(Centre_line.start_point, Centre_line.end_point, dxfattribs={'layer': 'CenterLines'})
        # Labelling SP and EP
        __debug_location(point=Centre_line.start_point, name='SP', radius=1, color=2)
        __debug_location(point=Centre_line.end_point, name='EP', radius=1, color=2)
        
    if output_file:
        dwg.layers.new(name='CenterLines', dxfattribs={'linetype': 'DASHED', 'color': 7})
        dwg.saveas(output_file)
        print(f'File {output_file} save success.')

def get_centre_lines(
    msp, dwg, layer_name, conversion_factor, 
        output_file = 'detected_centrelines.dxf', *args, **kwargs) -> List[CentreLine]:
    """This function returns Centre_lines from polylines present in the layer "PP-Centre_line"
    in the dxf file.

    Returns:
        List[Centre_line]: Returns a list of Centre_line line segments.
    """
    global MAXIMUM_DISTANCE_BETWEEN_CENTRE_LINES
    MAXIMUM_DISTANCE_BETWEEN_CENTRE_LINES = MAXIMUM_DISTANCE_BETWEEN_CENTRE_LINES * conversion_factor
    if "lines" in kwargs.keys() and kwargs['lines'] is not None:
        lines = preprocess_lines(kwargs['lines'])
    else:
        lines = get_lines(msp, dwg, layer_name)
    slope_bucket = get_slope_bucket(lines)
    parallel_line_pairs = get_parallel_line_pairs(slope_bucket)
    centre_lines = get_centre_lines_from_pairs(parallel_line_pairs)
    draw_Centre_lines(centre_lines, msp, dwg, output_file)
    return centre_lines
