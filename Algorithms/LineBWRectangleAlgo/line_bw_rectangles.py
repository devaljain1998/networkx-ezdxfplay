import sys
import ezdxf
import os
import pprint
import math
from pillarplus import math as ppmath

file_path = 'Algorithms/LineBWRectangleAlgo/input/DXF/'
input_file = 'RECTANGAL.dxf'
output_file_path = 'Algorithms/LineBWRectangleAlgo/output/'
input_file_name = input_file.split('.')[0]
output_file = f'{input_file_name}_output.dxf'

#Reading the file
try:
    dwg = ezdxf.readfile(file_path + input_file)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

msp = dwg.modelspace()
print(f'File read success from {file_path}.')    

# dxfattribs and properties accessed using .dxf
def print_entity(e):
    # properties common to all entities
    '''
    print(e.dxftype(), 'Type')
    print(e.dxf.layer, 'e.dxf.layer')
    print(e.dxf.handle, 'e.dxf.handle')
    print(e.dxf.linetype, 'e.dxf.linetype')
    print(e.dxf.ltscale, 'e.dxf.ltscale')
    '''
# all entities have certain properties according to their types
    if e.dxftype() == 'INSERT':  # block type
        print(e.dxf.name, 'e.dxf.name')

        # get OCS (coordinates)
        print(e.dxf.insert, 'e.dxf.insert')
        # get world coordinates (WCS)
        wcs_location = e.ocs().to_wcs(e.dxf.insert)
        print(wcs_location, 'WCS')

    if e.dxftype() == 'CIRCLE':
        print(e.dxf.center, 'e.dxf.center')
        print(e.dxf.radius, 'e.dxf.radius')

    if e.dxftype() == 'LWPOLYLINE':
        print(e.get_points(), 'e.dxf.points')

    if e.dxftype() == 'LINE':
        print(e.dxf.start, 'e.dxf.start')
        print(e.dxf.end, 'e.dxf.end')
        print(e.dxf.color, 'e.dxf.color')

    if e.dxftype() == 'ARC':
        # the arc goes from start_angle to end_angle
        # in counter clockwise direction
        print(e.dxf.center, 'e.dxf.center')
        print(e.dxf.radius, 'e.dxf.radius')
        print(e.dxf.start_angle, 'e.dxf.start_angle')
        print(e.dxf.end_angle, 'e.dxf.end_angle')

    if e.dxftype() == 'ELLIPSE':
        # the ellipse goes from start to end param
        # in counter clockwise direction
        # a full ellipse goes from 0 to 2*pi
        print(e.dxf.center, 'e.dxf.center')
        # endpoint of major axis, relative to the center
        print(e.dxf.major_axis, 'e.dxf.major_axis')
        print(e.dxf.ratio, 'e.dxf.ratio')
        print(e.dxf.start_param, 'e.dxf.start_param')
        print(e.dxf.end_param, 'e.dxf.end_param')

    if e.dxftype() == 'TEXT':
        print(e.dxf.text, 'e.dxf.text')		# returns a str
        print(e.dxf.insert, 'e.dxf.insert')
        print(e.dxf.height, 'e.dxf.height')
        print(e.dxf.rotation, 'e.dxf.rotation')
        print(e.dxf.width, 'e.dxf.width')

    if e.dxftype() == 'MTEXT':
        # To Do
        pass

    if e.dxftype() == 'SHAPE':
        print(e.dxf.name, 'e.dxf.name')
        print(e.dxf.insert, 'e.dxf.insert')
        print(e.dxf.size, 'e.dxf.size')
        print(e.dxf.rotation, 'e.dxf.rotation')

    if e.dxftype() == 'POLYLINE':
        print(e.dxf.elevation, 'e.dxf.elevation')
        print(e.dxf.flags, 'e.dxf.flags')
        print(e.dxf.m_count, 'e.dxf.m_count')
        print(e.dxf.n_count, 'e.dxf.n_count')

    if e.dxftype() == 'LWPOLYLINE':
        print(e.dxf.elevation, 'e.dxf.elevation')
        print(e.dxf.flags, 'e.dxf.flags')
        print(e.dxf.const_width, 'e.dxf.const_width')
        print(e.dxf.count, 'e.dxf.count')

    if e.dxftype() == 'SOLID' or e.dxftype() == 'TRACE':
        print(e.dxf.vtx0, 'e.dxf.vtx0')
        print(e.dxf.vtx1, 'e.dxf.vtx1')
        print(e.dxf.vtx2, 'e.dxf.vtx2')
        print(e.dxf.vtx3, 'e.dxf.vtx3')

    if e.dxftype() == 'HATCH':
        '''
        print(e.get_seed_points(),'e.get_seed_points()')
        print(e.dxf.pattern_name, 'e.dxf.pattern_name')		# returns a str
        print(e.dxf.solid_fill, 'e.dxf.solid_fill')
        print(e.dxf.pattern_angle, 'e.dxf.pattern_angle')
        '''
        with e.edit_boundary() as boundary:
            for p in boundary.paths:
                pass
                # To DO
                '''
				if isinstance(p, ezdxf.modern.hatch.PolylinePath):
					print(p.vertices, 'PolylinePath')
					print(p.is_closed, 'PolylinePath.is_closed')

				else:
					for edge in p.edges:
						if isinstance(edge, ezdxf.modern.hatch.LineEdge):
							print(edge.start, 'EdgePath start')
							print(edge.end, 'EdgePath end')
				'''
    #print(e.dxf.thickness, 'e.dxf.thickness')
    #print(e.dxf.true_color, 'e.dxf.true_color')
    #print(e.dxf.color_name, 'e.dxf.color_name')
    print('###########')
    
    
# print('printing all the layers:')
# for layer in dwg.layers:
#     print(layer)

# Printing all the elements:
# for e in msp:
#     print_entity(e)

print('Printing all the polyines:')
#fetching all the polylines from the layer PP-BEAM
polylines = msp.query('LWPOLYLINE[layer=="PP-BEAM"]')
for polyline in polylines:
    print_entity(polyline)
    
def is_closed(polyline):
    CLOSED = 1
    return CLOSED == polyline.dxf.flags

#Convert polylines into lines:
print('Converting polylines into lines.')
lines = []
line_meta = {}
for polyline in polylines:
    line = []
    
    for point in polyline:
        x, y = point[0], point[1]
        line.append((x, y))
        
        #if the line has two points:
        if len(line) == 2:
            #Check if the line is decreasing or not:
            if ppmath.is_line_decreasing_on_x_2d(line):
                #Swap the points if the line is decreasing:
                line.reverse()
            
            #Append the line into lines
            lines.append(line)
            line_meta[str(line)] = {'polyline' : polyline}
            
            #clear the line
            line = [(x, y)]
    
    # if the polyline is closed 
    if ppmath.is_polyline_closed(polyline):
        #Connecting the first and last points also:
        p1 = polyline[-1]
        x1, y1 = p1[0], p1[1]
        p2 = polyline[0]
        x2, y2 = p2[0], p2[1]
        line = [(x1, y1), (x2, y2)]
        line_meta[str(line)] = {'polyline' : polyline}
        lines.append(line)

print('Lines:')            
pprint.pprint(lines)
print('Line_meta:')
pprint.pprint(line_meta)


def try_to_build_the_exact_figure(lines):
    dwg.layers.new('TestFigure')
    for line in lines:
        print(f'Adding line {line}')
        p1 = line[0]
        p2 = line[1]
        msp.add_line(p1, p2, dxfattribs={'layer': 'TestFigure'})
        
# try_to_build_the_exact_figure(lines)

print('\n\nLines after sorting:')
lines.sort()
pprint.pprint(lines)
    
def get_slope(x1, y1, x2, y2): 
    try:
        slope = (float)(y2-y1)/(float)(round(x2-x1))
    except ZeroDivisionError:
        print(f'Zerodivisionerror:: Variables are: {(x1, y1), (x2, y2)}')
        return math.inf
    return slope

def test_rounding_slopes_of_lines():
    for line in lines:
        p1, p2 = line[0], line[1]
        slope = ppmath.find_slope(p1, p2)


slopes = dict()
#Finding slopes of every line:
for line in lines:
    p1, p2 = line[0], line[1]
    slope = get_slope(p1[0], p1[1], p2[0], p2[1])# slope = ppmath.find_slope(p1, p2)
    
    #Rounding slope for 3 decimal:
    if slope != math.inf:
        slope = round(slope) #slope = round(slope, ndigits = 5)
    
    # Check if the slope exists in the slope_dict
    if slope in slopes.keys():
        slopes[slope].append(line)
    else:
        slopes[slope] = [line]
    #print(f'Slope of {line} : {slope}')

print('\n\n====Printing the lines slopes:\n')    
pprint.pprint(slopes)

def get_distance_of_all():
    print('Printing all the distance of lines:')
    for slope, lines in slopes.items():
        print(f'Printing dis for slope: {slope}')
        for i in range(len(lines)):
            line1 = lines[i]
            for j in range(i + 1, len(lines)):
                line2 = lines[j]
                distance = ppmath.get_distance_between_two_parallel_lines(line1, line2)
                print(f'Distance {distance} b/w {line1, line2}')
            print('\n\n')
            
# get_distance_of_all()

def does_lines_belong_to_same_polyline(line1, line2) -> bool:
    return line_meta[str(line1)]['polyline'] == line_meta[str(line2)]['polyline']

# loop through lines of each slope and draw a line in the centre
parallel_line_pairs = []
for slope, lines in slopes.items():
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
            distance = ppmath.get_distance_between_two_parallel_lines(line1, line2)
            print(f'Dist: {distance} for {line1, line2}')
            
            #edge cases:
            # Lines should not fall into each other
            if round(distance) == 0: 
                counter += 1
                line2 = _get_line2(index, counter)
                continue
            
            # Lines should be overlapping
            if not ppmath.are_lines_overlapping(line1, line2, slope):
                counter += 1
                line2 = _get_line2(index, counter)
                continue                
            
            # Lines should be inside a threshold
            if distance > ppmath.MAXIMUM_DISTANCE_BETWEEN_BEAMS: 
                # break            
                counter += 1
                line2 = _get_line2(index, counter)
                continue                
                
            if does_lines_belong_to_same_polyline(line1, line2):
                counter += 1
                line2 = _get_line2(index, counter)
                continue                                
            
            print(f'Forming a pair b/w {line1, line2}, slope: {slope}\n')
            #Make pair of these lines
            parallel_line_pairs.append((line1, line2))
            
            counter += 1
            line2 = _get_line2(index, counter)
            
        i +=1
        
print(f'Parallel line pairs:')
pprint.pprint(parallel_line_pairs)

#Create a new layer for center-lines
dwg.layers.new(name='CenterLines', dxfattribs={'linetype': 'DASHED', 'color': 7})
        
#Now loop through the pairs and draw a line to center of these pairs:
print('\nLooping through pairs now:\n')

def get_centre_points(line1, line2):
    #Start center points:
    x1 = (line1[0][0] + line2[0][0]) / 2
    y1 = (line1[0][1] + line2[0][1]) / 2

    #End center points:
    x2 = (line1[1][0] + line2[1][0]) / 2
    y2 = (line1[1][1] + line2[1][1]) / 2
    return x1, y1, x2, y2


def get_direction(line_to_be_moved, other_line):
    # fetch the highest point 
    max_point = max(line_to_be_moved[0], line_to_be_moved[1])
    
    directions = {1 : "RIGHT", -1 : "LEFT", 0 : "ON THE LINE"}
    
    from ezdxf.math import Vec2, point_to_line_relation
    dir = point_to_line_relation(Vec2(max_point), Vec2(other_line[0]), Vec2(other_line[1]))
    
    print(f'Direction for {line_to_be_moved, other_line} is {directions[dir]}')
    
    return dir

def get_gfg_direction(line_to_be_moved, other_line):
    # fetch the highest point 
    max_point = max(line_to_be_moved[0], line_to_be_moved[1])
    
    directions = {1 : "RIGHT", -1 : "LEFT", 0 : "ON THE LINE"}
    from ezdxf.math import Vec2
    A = Vec2(other_line[0])
    B = Vec2(other_line[1])
    P = Vec2(max(line_to_be_moved[0], line_to_be_moved[1]))
    
    B.x -= A.x; 
    B.y -= A.y; 
    P.x -= A.x; 
    P.y -= A.y; 
    
    cross_product = B.x * P.y - B.y * P.x
    
    RIGHT, LEFT, ZERO = 1, -1, 0
    
    if (cross_product > 0):
        return RIGHT; 
  
    #return LEFT if cross product is negative 
    if (cross_product < 0):
        return LEFT; 
  
    #return ZERO if cross product is zero.  
    return ZERO;    

def get_non_segmented_lines(line1, line2):
    #Start center points:
    x1, y1, x2, y2 = get_centre_points(line1, line2)
    
    print(f"""
            line1 : {line1},
            line2 : {line2},
            centre_points: {(x1, y1), (x2, y2)}
            """)
    
    # Find out when the centre points are coming as equal:
    if (x1, y1) == (x2, y2):
        print(f'In this case IT IS NOT A LINE, JUST A POINT: {(x1, y1, (x2, y2))}')
        
        # Reversing line 2 in this case and then check if the points are still the same
        l2 = list(reversed(line2))
        x1, y1, x2, y2 = get_centre_points(line1, l2)
        
    return [(x1, y1), (x2, y2)]
    
    # Adding a new center line with the layer: CenterLines
    msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'CenterLines'})
    
    
debug_parallel_line_pairs = []    

def get_segmented_line(line1, line2):
    """This function returns a line segment in between the two the parallel line pairs.
    Logic has been taken from MathStackExchange (link given below).
    Reference: 
        https://math.stackexchange.com/questions/2593627/i-have-a-line-i-want-to-move-the-line-a-certain-distance-away-parallelly/2594547

    Args:
        line1 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
        line2 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
        
    Returns:
        line (List of Tuples): A linesegment in middle of line1 and line2.
    """
    RIGHT = 1
    LEFT = -1
    
    # Calculate lenght of both the line segment.
    line1_length = ppmath.get_length_of_line_segment(line1)
    line2_length = ppmath.get_length_of_line_segment(line2)
        
    print(f'l1s: {line1_length}, l2s: {line2_length}')
    # The line to be moved is the line which is the smaller between the two
    if min(line1_length, line2_length) == line1_length:
        line_to_be_moved = line1
        r = line1_length
        print(f'LinetobeMoved: {line_to_be_moved}, r: {r}')
        direction = get_direction(line_to_be_moved, line2)
        debug_parallel_line_pairs.append({'lines' : (line1, line2), 'DIR' : direction})
    else:
        line_to_be_moved = line2
        r = line2_length
        direction = get_direction(line_to_be_moved, line1)
        debug_parallel_line_pairs.append({'lines' : (line1, line2), 'DIR' : direction})
        
    # Make a new line which is at half the distance between line1 and line2
    distance = ppmath.get_distance_between_two_parallel_lines(line1, line2)
    
    # Get direction and distance with which the line is needed to move

    d = distance / 2
    
    # Formula to calculate the points of the lines
    x1, y1, x2, y2 = ppmath.get_line_points_2d(line_to_be_moved)
    multiplier = d / r
    del_x = multiplier * (y1 - y2)
    del_y = multiplier * (x2 - x1)
    
    x3 = x1 + del_x if direction == RIGHT else x1 - del_x
    y3 = y1 + del_y if direction == RIGHT else y1 - del_y
    x4 = x2 + del_x if direction == RIGHT else x2 - del_x
    y4 = y2 + del_y if direction == RIGHT else y2 - del_y
    
    return [(x3, y3), (x4, y4)]

def get_centered_line_segments(line1, line2) -> list:
    """Function which returns a centered line segments from parallel pairs.

    Args:
        line1 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
        line2 (List of Tuples): A line is a collection of tuple of points in the following manner [(x1, y1), (x2, y2)].
        
    Returns:
        line (List of Tuples): A linesegment in middle of line1 and line2.
    """
    # Calculate lenght of both the line segment.
    line1_length = ppmath.get_length_of_line_segment(line1)
    line2_length = ppmath.get_length_of_line_segment(line2)
    
    smaller_line = line1 if line1_length <= line2_length else line2
    bigger_line = line1 if smaller_line == line2 else line2
    
    # We need to get perpendicular points from the smaller line to the bigger line
    p1 = smaller_line[0]
    perpendicular_point1 = ppmath.find_perpendicular_point(p1, bigger_line[0], bigger_line[1])
    
    # Check if the perpendicular point exists on the other line or not:
    if ppmath.is_between(perpendicular_point1, bigger_line[0], bigger_line[1]):
        # Find centre point in this case
        centre_point1 = ppmath.get_mid_points_between_points(p1, perpendicular_point1)
    else:
        # we need to get the point from the bigger line now
        for point in bigger_line:
            perpendicular_point1 = ppmath.find_perpendicular_point(point, smaller_line[0], smaller_line[1])
            # if this perpendicular point lies in the smaller line then break
            if ppmath.is_between(perpendicular_point1, smaller_line[0], smaller_line[1]):
                # calculate the centre point first
                centre_point1 = ppmath.get_mid_points_between_points(point, perpendicular_point1)                
                break
                
    # We need to get perpendicular points from the smaller line to the bigger line
    p2 = smaller_line[1]
    perpendicular_point2 = ppmath.find_perpendicular_point(p2, bigger_line[0], bigger_line[1])
    
    # Check if the perpendicular point exists on the other line or not:
    if ppmath.is_between(perpendicular_point2, bigger_line[0], bigger_line[1]):
        # Find centre point in this case
        centre_point2 = ppmath.get_mid_points_between_points(p2, perpendicular_point2)
    else:
        # we need to get the point from the bigger line now
        for point in bigger_line:
            perpendicular_point2 = ppmath.find_perpendicular_point(point, smaller_line[0], smaller_line[1])
            # if this perpendicular point lies in the smaller line then break
            if ppmath.is_between(perpendicular_point2, smaller_line[0], smaller_line[1]):
                # calculate the centre point first
                centre_point2 = ppmath.get_mid_points_between_points(point, perpendicular_point2)
                break
            
    return [centre_point1, centre_point2]
    
    
for pair in parallel_line_pairs:
    line1, line2 = pair
    
    if line2:
        x1, y1, x2, y2 = ppmath.get_line_points_2d(line1)
        
        if slope != math.inf:
            try:
                slope = round(get_slope(x1, y1, x2, y2))
            except OverflowError as oe:
                print(oe)
                print('slope', slope)
            
        print(f'Now calculating line segment {line1, line2}')
        
        # if slope == 0 or slope == math.inf:
        #     line_segment = get_non_segmented_lines(line1, line2)
        # else:
        #     line_segment = get_segmented_line(line1, line2)
            
        
        line_segment = get_centered_line_segments(line1, line2)
        
        print(f"""
              line1: {line1},
              line2: {line2},
              line_segment: {line_segment}\n\n
              """)
        
        msp.add_line(line_segment[0], line_segment[1], dxfattribs={'layer': 'CenterLines'})
        
print('Debug_parallel_line_pairs')
pprint.pprint(debug_parallel_line_pairs)
        
print('Success now saving the file')
#Saving the final file:
dwg.saveas(output_file_path + output_file)
print(f'File {output_file_path + output_file} save success.')