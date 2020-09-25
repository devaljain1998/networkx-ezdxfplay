import sys
import ezdxf
import os
import pprint
import math
from pillarplus import math as ppmath

print(f'{ppmath}')

file_path = 'Algorithms/LineBWRectangleAlgo/input/DXF/'
input_file = 'sample1.dxf'
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
for polyline in polylines:
    line = []
    
    for point in polyline:
        x, y = point[0], point[1]
        line.append((x, y))
        
        #if the line has two points:
        if len(line) == 2:
            #Append the line into lines
            lines.append(line)
            #clear the line
            line = [(x, y)]
    
    # if the polyline is closed 
    if ppmath.is_polyline_closed(polyline):
        #Connecting the first and last points also:
        p1 = polyline[-1]
        x1, y1 = p1[0], p1[1]
        p2 = polyline[0]
        x2, y2 = p2[0], p2[1]
        lines.append([(x1, y1), (x2, y2)])

print('Lines:')            
pprint.pprint(lines)


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
        return 'INFINITE'
    return slope

slopes = dict()
#Finding slopes of every line:
for line in lines:
    p1, p2 = line[0], line[1]
    slope = ppmath.find_slope(p1, p2)
    
    #Rounding slope for 3 decimal:
    if type(slope) == float:
        slope = round(slope, 5) #slope = round(slope, ndigits = 5)
    
    # Check if the slope exists in the slope_dict
    if slope in slopes.keys():
        slopes[slope].append(line)
    else:
        slopes[slope] = [line]
    #print(f'Slope of {line} : {slope}')

print('\n\n====Printing the lines slopes:\n')    
pprint.pprint(slopes)


# loop through lines of each slope and draw a line in the centre
parallel_line_pairs = []
for slope, lines in slopes.items():
    print(f'Looping for slope : {slope}:\n')
    
    # fetch points in pair of two and form their pairs:
    index, i = 0, 0
    while (2 * i < len(lines)):
        index = 2 * i
        line1 = lines[index]
        if index + 1 < len(lines):
            line2 = lines[index + 1]
        else:
            line2 = None
        #Make pair of these lines
        if line2:
            print(f'Found a parallel line pair. {line1, line2}')
            print(f'Distance between them: {ppmath.get_distance_between_two_parallel_lines(line1, line2)}')
            parallel_line_pairs.append((line1, line2))
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

for pair in parallel_line_pairs:
    line1, line2 = pair
    
    if line2:
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
            
            #Reversing line 2 in this case and then check if the points are still the same
            line2.reverse()
            x1, y1, x2, y2 = get_centre_points(line1, line2)
        
        # Adding a new center line with the layer: CenterLines
        msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'CenterLines'})
    
print('Success now saving the file')
#Saving the final file:
dwg.saveas(output_file_path + output_file)
print(f'File {output_file_path + output_file} save success.')