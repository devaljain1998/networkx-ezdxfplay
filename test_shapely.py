import json
import math
import pprint
from typing import List, Tuple, Union

import ezdxf
import networkx as nx
import shapely
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

from centre_lines import CentreLine
from pillarplus.math import (directed_points_on_line, find_angle,
                             find_distance, find_intersection_point_1,
                             find_mid_point, find_rotation,
                             get_nearest_lines_from_a_point, is_between,
                             find_perpendicular_point)
from Shapely_polygons.shapely_polygons import pointslist_from_lines, define_polygons, find_polygon_area
from collections import OrderedDict

# DEBUG:
def __debug_location(msp, point, name: str = 'debug', radius = 2, color:int = 2, char_height=0.5, layer: str = 'debug'):
    msp.add_circle(point, radius, dxfattribs={'color': color, 'layer': layer})
    mtext = msp.add_mtext(name, dxfattribs = {'layer': layer})
    mtext.set_location(point)
    mtext.dxf.char_height = char_height



# print('windows:', len(windows))

# print('doors:', len(doors))

# all_doors = list(filter(lambda entity: entity['type']=='door', identification_json['entities']))
def debug_display_all_windows_and_doors():
    dwg = ezdxf.new()
    msp = dwg.modelspace()
    
    # Adding edges from the graph
    for edge in graph.edges:
        msp.add_line(edge[0], edge[1], dxfattribs={'layer': 'walls'})
    
    for window in windows:
        window_location = window['location']
        msp.add_circle(window_location, radius=1, dxfattribs={'color':2})
        window_text = msp.add_mtext(f'W{window["category"]}')
        window_text.set_location(window_location)
        window_text.dxf.char_height = 0.3

    for ix, door in enumerate(doors): #all_doors
        door_location = door['location']
        msp.add_circle(door_location, radius=1, dxfattribs={'color':2})
        door_text = msp.add_mtext(f'D{door["category"]}{ix + 1}')
        door_text.set_location(door_location)
        door_text.dxf.char_height = 0.3
        
    dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/only_windows_and_doors_points.dxf')
    print('Windows and doors file saved at:', f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/only_windows_and_doors_points.dxf')
    exit()
# debug_display_all_windows_and_doors()

### HELPER FUNCTION:
centre_line_tree = None
def fill_str_tree(centre_lines):
    lines = []
    for centre_line in centre_lines:
        line = LineString([centre_line.start_point, centre_line.end_point])
        lines.append(line)
    global centre_line_tree
    centre_line_tree = STRtree(lines)
    print('Tree builded.')

def is_angle_is_180_or_0_degrees(angle: Union[float, int], buffer: float = None) -> bool:
    from math import pi
    if type(angle) == int:
        return 179 <= angle <= 181 or -1 <= angle <= 1
    if buffer:
        return (pi - buffer) <= angle <= (pi + buffer) or buffer <= angle <= -buffer
    return (pi - 0.1) <= angle <= (pi + 0.1) or 0.1 <= angle <= -0.1

def break_edge_into_two_edges(edge, node, graph):
    # Fetch points from edge
    p1, p2 = edge
    # Create new edges
    new_edges = [(p1, node), (node, p2)]
    graph.add_edges_from(new_edges)
    # Delete the current edge
    graph.remove_edge(edge[0], edge[1])
    return


def get_nearest_centre_lines_from_a_point(
        point: tuple, centre_lines: List["CentreLine"], entity_location: tuple) -> List["CentreLine"]:
    """
    The function returns nearest centre_lines to a point.
    """
    centre_line_dict = {(centre_line.start_point, centre_line.end_point):centre_line for centre_line in centre_lines}
    nearest_lines = get_nearest_lines_from_a_point(point = point, lines = list(centre_line_dict.keys()))

    index = 0
    # DEBUG
    conversion_factor = 0.0393701
    DISTANCE_FOR_WALL_WITH_ENTITY = 100 * conversion_factor
    query = Point(entity_location).buffer(DISTANCE_FOR_WALL_WITH_ENTITY)
    # Check whether the starting lines are not too close for the entity_location    
    close_lines_to_the_entity_location = centre_line_tree.query(query)
    if len(close_lines_to_the_entity_location) > 0:
        for close_line in close_lines_to_the_entity_location:
            print(f"counter: {counter}", "increasing the index and neglecting the close centre_line")
            close_line_coords = tuple(close_line.coords)
            item_index = nearest_lines.index(close_line_coords)
            index = item_index + 1
    
    # Now map the nearest lines to the values of centrelines:
    nearest_lines = list(map(lambda nearest_line: centre_line_dict[nearest_line], nearest_lines))
    
    # DEBUG:
    shapely_point = Point(point)
    import ezdxf
    _dwg = ezdxf.new()
    _msp = _dwg.modelspace()
    _msp.add_circle(entity_location, radius=0.2, dxfattribs={'layer': 'entity_location'})
    loc_text = _msp.add_mtext(f'{int(entity_location[0])}, {int(entity_location[1])}', dxfattribs={'layer':'debug'})
    loc_text.set_location(entity_location)
    loc_text.dxf.char_height = 0.2
    
    for idx, line in enumerate(nearest_lines):
        shapely_line = LineString([line.start_point, line.end_point])
        distance = shapely_point.distance(shapely_line)
        _msp.add_line(line.start_point, line.end_point, dxfattribs={'layer':'centrelines'})
        mtext = _msp.add_mtext(f'{idx} {distance}', dxfattribs={'layer':'centrelines'})
        mtext.set_location(find_mid_point(line.start_point, line.end_point))
        mtext.dxf.char_height = 0.3
    for edge in graph.edges:
        _msp.add_line(edge[0], edge[1], dxfattribs={'layer':'wall'})
    
    # label the chosen lines:
    n1, n2 = nearest_lines[index], nearest_lines[index+1]
    for n in (n1, n2):
        mtext = _msp.add_mtext('chosen', dxfattribs={
                              'layer': 'chosen_line', 'color': 3})
        mtext.set_location(find_mid_point(n.start_point, n.end_point))
        mtext.dxf.char_height = 0.5
    
    _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/nearest_centre_lines_{counter}.dxf')
    print('Done saving nearest line', f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/nearest_centre_lines_{counter}.dxf')
    # import sys
    # sys.exit(1)    
    
    return nearest_lines[index], nearest_lines[index + 1]



# labels:
PARALLEL = "PARALLEL"
PERPENDICULAR = "PERPENDICULAR"

# DEBUG:
extra_data = {}

graph = None
input_key = None
counter = 0
def preprocess_module(*args, **kwargs):
    global graph, input_key, counter
    graph = kwargs['graph']
    input_key = kwargs['input_key']
    counter = kwargs['counter']


def extend_wall_lines_for_entity(entity: dict, centre_lines: List["CentreLine"], graph: "nx.Graph", *args, **kwargs):
    """This function extends the wall_lines(edges) and updates the graph by the extending the walls for that entity.
    
    Procedure:
        1. Do some exception handling to check the type of the entity is "door" or "window".
        2. Get entity location:
            entity_location = entity["location"]
        3. Get nearest centre lines to that entity:
            nearest_centre_lines = get_nearest_lines_to_a_point(point = entity_location, lines = centre_lines)
        4. For the first two nearest lines, extend the wall:
            extended_lines = get_extended_wall_lines_with_nearest_lines(graph, nearest_line1, nearest_line2)
        5. Adjust the extended lines:
            adjust_extend_lines(graph, entity_location, extended_lines)
        6. return

    Args:
        entity (dict: "Entity"): Either of type "door" or "wall".
        centre_lines (current centrelines): current centrelines generated from the graph.
        graph (nx.Graph): A networkx graph.
    """
    def get_extended_wall_lines_with_nearest_lines(
        entity_location: float, graph: 'nx.Graph', nearest_line1: "CentreLine", nearest_line2: "CentreLine", **kwargs) -> List[tuple]:
        """This function extends the walls by taking in the input two nearest lines.
        
        Procedure:
            1. label both the nearest lines as "parallel" or "perpendicular".
                1.1 by looping each line: nearest_line
                1.2 getting the closest point of the nearest line.
                1.3 find the angle from the point, closest_point, distant_point
                1.4 if the angle is approx(0 | 180) degree then label it is as "parallel"
                    otherwise "perpendicular".
            2. for parallel line: get_directed_points for width / 2 and those are the end points of the new lines, (rotation + 90) of the nearest line.
            3. for perpendicular line: 
                3.1 perp_point = get_directed_point for width / 2 which is near to the point
                3.2 end_points =  get_directed_points for width / 2, perp_point, rotation of the nearest_line
            4. now just match both the end points to form lines:
                end_points = match_both_the_end_points(l1, l2, r1, r2)
            5. return end_points
            
        Args:
            entity_location (float)
            graph (nx.Graph)
            nearest_line1 ("CentreLine"): nearest_line[0]
            nearest_line2 ("CentreLine"): nearest_line[1]
        """
        def get_end_points(nearest_line1: 'CentreLine', nearest_line2: 'CentreLine', entity_location: float) -> List[List[tuple]]:
            """This function calculates the end_points and returns it from both the nearest lines.
            Returns:
                List[List[tuple]]: Returns a set of end-points: [nearest_line1_end_point, nearest_line2_end_point2]
            """
            def get_end_points_for_both_parallel_lines(nearest_line1: 'CentreLine', nearest_line2: 'CentreLine', entity_location: float):
                # Exception Handling:
                if not {nearest_line1.type, nearest_line2.type} == {PARALLEL}:
                    raise AttributeError(
                        f'The function is only meant for parallel lines but got: {nearest_line1.type, nearest_line2.type}.')
                    
                # find width of the smallest parallel_line:
                smallest_parallel_line_width = nearest_line1.width if nearest_line1.width <= nearest_line2.width else nearest_line2.width
                
                end_point_sets = []
                # Use this width to find the end-points of the parallel and perpendicular lines
                # Now find the end_points of each nearest_line:
                for nearest_line in (nearest_line1, nearest_line2):
                    closest_point = nearest_line.get_closest_point(entity_location)
                    distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.end_point
                    rotation = find_rotation(closest_point, distant_point)
                    
                    # get the end_points:
                    nearest_line_end_point_rotation = math.radians(rotation + 90)
                    nearest_line_end_points = directed_points_on_line(
                        closest_point, nearest_line_end_point_rotation, nearest_line.width / 2)
                    end_point_sets.append(set(nearest_line_end_points))
                
                return end_point_sets

            def get_end_points_for_mixed_lines(nearest_line1: 'CentreLine', nearest_line2: 'CentreLine', entity_location: float):
                # Exception Handling:
                if not {nearest_line1.type, nearest_line2.type} == {PARALLEL, PERPENDICULAR}:
                    raise AttributeError(
                        f'The function is only meant for parallel and perpendicular lines but got: {nearest_line1.type, nearest_line2.type}.')
                
                # find parallel and perpendicular lines:
                parallel_line = nearest_line1 if nearest_line1.type == PARALLEL else nearest_line2
                perpendicular_line = nearest_line1 if nearest_line1.type == PERPENDICULAR else nearest_line2
                
                # find width of the parallel_line:
                parallel_line_width = parallel_line.width
                end_point_sets = []
                # Use this width to find the end-points of the parallel and perpendicular lines
                # Now find the end_points of each nearest_line:
                for nearest_line in (nearest_line1, nearest_line2):
                    closest_point = nearest_line.get_closest_point(entity_location)
                    distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.end_point
                    rotation = find_rotation(closest_point, distant_point)
                    
                    if nearest_line.type == PARALLEL:
                        # get the end_points:
                        nearest_line_end_point_rotation = math.radians(rotation + 90)
                        nearest_line_end_points = directed_points_on_line(
                            closest_point, nearest_line_end_point_rotation, parallel_line_width / 2)
                        end_point_sets.append(set(nearest_line_end_points))
                    # for perpendicular
                    else:
                        perpendicular_point_on_the_centre_line = find_perpendicular_point(
                                            center=entity_location, line_start=closest_point, line_end=distant_point)
                        perp_points = directed_points_on_line(
                            perpendicular_point_on_the_centre_line, math.radians(rotation + 90), nearest_line.width / 2)
                        closest_perp_point = perp_points[0] if \
                            find_distance(entity_location, perp_points[0]) <= find_distance(entity_location, perp_points[1]) else perp_points[1]
                        nearest_line_end_points = directed_points_on_line(
                            closest_perp_point, math.radians(rotation), parallel_line_width / 2)
                        end_point_sets.append(set(nearest_line_end_points))
                        
                        # DEBUG
                        __debug_location(
                            msp=_msp,
                            point=perpendicular_point_on_the_centre_line,
                            name='PERPPOINT',
                            radius=1,
                            color=4,
                            char_height=0.3
                        );
                        __debug_location(
                            msp=_msp,
                            point=closest_perp_point,
                            name='CPP',
                            radius=0.2,
                            color=2,
                            char_height=0.3
                        );                
                        __debug_location(
                            msp=_msp,
                            point=nearest_line_end_points[0],
                            name='nlep1',
                            radius=0.2,
                            color=5,
                            char_height=0.3
                        );                
                        __debug_location(
                            msp=_msp,
                            point=nearest_line_end_points[1],
                            name='nlep2',
                            radius=0.2,
                            color=5,
                            char_height=0.3
                        );                
                        
                        
                return end_point_sets
                

            def get_end_points_for_both_perpendicular_lines(nearest_line1: 'CentreLine', nearest_line2: 'CentreLine', entity_location: float):
                # Exception Handling:
                if not {nearest_line1.type, nearest_line2.type} == {PERPENDICULAR}:
                    raise AttributeError(
                        f'The function is only meant for perpendicular lines but got: {nearest_line1.type, nearest_line2.type}.')
                                
                # find width of the parallel_line:
                smallest_perpendicular_line_width = nearest_line1.width if nearest_line1.width <= nearest_line2.width else nearest_line2.width
                end_point_sets = []
                # Use this width to find the end-points of the parallel and perpendicular lines
                # Now find the end_points of each nearest_line:
                for nearest_line in (nearest_line1, nearest_line2):
                    closest_point = nearest_line.get_closest_point(entity_location)
                    distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.end_point
                    rotation = find_rotation(closest_point, distant_point)
                    
                    perpendicular_point_on_the_centre_line = find_perpendicular_point(
                                        center=entity_location, line_start=closest_point, line_end=distant_point)
                    perp_points = directed_points_on_line(
                        perpendicular_point_on_the_centre_line, math.radians(rotation + 90), nearest_line.width / 2)
                    closest_perp_point = perp_points[0] if \
                        find_distance(entity_location, perp_points[0]) <= find_distance(entity_location, perp_points[1]) else perp_points[1]
                    nearest_line_end_points = directed_points_on_line(
                        closest_perp_point, math.radians(rotation), smallest_perpendicular_line_width / 2)
                    end_point_sets.append(set(nearest_line_end_points))
                    
                    # DEBUG
                    __debug_location(
                        msp=_msp,
                        point=perpendicular_point_on_the_centre_line,
                        name='PERPPOINT',
                        radius=1,
                        color=4,
                        char_height=0.3
                    );
                    __debug_location(
                        msp=_msp,
                        point=closest_perp_point,
                        name='CPP',
                        radius=0.2,
                        color=2,
                        char_height=0.3
                    );                
                    __debug_location(
                        msp=_msp,
                        point=nearest_line_end_points[0],
                        name='nlep1',
                        radius=0.2,
                        color=5,
                        char_height=0.3
                    );                
                    __debug_location(
                        msp=_msp,
                        point=nearest_line_end_points[1],
                        name='nlep2',
                        radius=0.2,
                        color=5,
                        char_height=0.3
                    );                
                        
                        
                return end_point_sets

            
            # Fill wall_counter dict: (used to keep the count of no of parallel or perpendicular walls.)
            wall_counter_dict = OrderedDict.fromkeys((PARALLEL, PERPENDICULAR), value=0)
            for nearest_line in (nearest_line1, nearest_line2):
                wall_counter_dict[nearest_line.type] += 1
                            
            end_point_function_mapper = {
                ((PARALLEL, 2), (PERPENDICULAR, 0)): get_end_points_for_both_parallel_lines,
                ((PARALLEL, 1), (PERPENDICULAR, 1)): get_end_points_for_mixed_lines,
                ((PARALLEL, 0), (PERPENDICULAR, 2)): get_end_points_for_both_perpendicular_lines,
            }
            
            end_point_function = end_point_function_mapper[tuple(sorted(wall_counter_dict.items()))]
            
            end_point_sets = end_point_function(
                nearest_line1=nearest_line1, nearest_line2=nearest_line2, entity_location=entity_location)
            
            #Exception Handling for end_point_sets:
            assert len(end_point_sets) == 2,\
                f"end_point_sets length should be 2 but got: {end_point_sets} for nearest_lines: {(nearest_line1, nearest_line2)}."

            # Clean end_point_sets
            # mapping sets to int
            end_point_sets[0] = set(map(lambda point: (int(point[0]), int(point[1])), end_point_sets[0]))
            end_point_sets[1] = set(map(lambda point: (int(point[0]), int(point[1])), end_point_sets[1]))
            
            return end_point_sets

        
        def match_both_end_points(left_point1, left_point2, right_point1, right_point2):
            """This function should take in the points and should return the end_points in the following order like:
            left_point1 ------------- right_point1
            left_point2 ------------- right_point2
            (forms a straight line).
            
            Procedure:
                1. Create a left_point_set = {left_end_point1, left_end_point2}
                2. Create a right_point_set = {right_end_point1, right_end_point2}
                3. Create a polygon out of those 4 points (using convex hull):
                    polygon = convex_hull([left_point1, left_point2, right_point1, right_point2])
                4. loops over the polygon coordinates, [Loop until len(end_points) == 2]
                    4.1 if the p1, p2 belong to the same set of points then reject
                    4.2 otherwise add it into the end_points 2
                5. return end_points

            Args:
                left_point1
                left_point2
                right_point1
                right_point2
            """
            
            # 1. Create a left_point_set = {left_point1, left_point2}
            left_point_set = {left_point1, left_point2}
            # 2. Create a right_point_set = {right_point1, right_point2}
            right_point_set = {right_point1, right_point2}
            # 3. Create a polygon out of those 4 points (using convex hull):
            #     polygon = convex_hull([left_point1, left_point2, right_point1, right_point2])
            from shapely.geometry import MultiPoint
            multi_point = MultiPoint([left_point1, left_point2, right_point1, right_point2])
            polygon = multi_point.convex_hull
            polygon_coordinates = list(polygon.exterior.coords)
            
            end_points = []
            for i in range(len(polygon_coordinates) - 1):
                # Exit condition:
                if len(end_points) == 2:
                    break
                # Logic
                point, next_point = polygon_coordinates[i], polygon_coordinates[i + 1]
                
                # 4.1 if the p1, p2 belong to the same set of points then reject
                if (point in left_point_set and next_point in left_point_set) or (point in right_point_set and next_point in right_point_set):
                    continue
                else:
                    end_points.append((point, next_point))
            
            # exception handling:
            if len(end_points) != 2:
                raise ValueError(
                    f"The points provided for the endpoints are not forming the endpoints or any polygons for the points: {(left_point1, left_point2, right_point1, right_point2)}.")
                
            # Cleaning endpoints before returning:
            # Converting them into int:
            end_points[0] = tuple(map(lambda point: (int(point[0]), int(point[1])), end_points[0]))
            end_points[1] = tuple(map(lambda point: (int(point[0]), int(point[1])), end_points[1]))

            return end_points
        
        
        # 1. label both the nearest lines as "parallel" or "perpendicular".
        # 1.1 by looping each line: nearest_line
        for nearest_line in (nearest_line1, nearest_line2):
            closest_point = nearest_line.get_closest_point(entity_location)
            distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.end_point
            # angle between entity location and closest point
            angle = find_angle(entity_location, closest_point, distant_point)
            
            nearest_line.type = PARALLEL if is_angle_is_180_or_0_degrees(angle) else PERPENDICULAR
            nearest_line.type_angle = angle
            
        # DEBUG:
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace()
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1])
        __debug_location(
            msp= _msp,
            point= entity_location,
            name='EL',
            radius=0.2,
            color=3,
            char_height=0.3
        )
        __debug_location(
            msp = _msp, 
            point = find_mid_point(nearest_line1.start_point, nearest_line1.end_point),
            name= f'{nearest_line1.type} {int(math.degrees(nearest_line1.type_angle))}',
            radius=3,
            color=5
        )
        __debug_location(
            msp = _msp, 
            point = find_mid_point(nearest_line2.start_point, nearest_line2.end_point),
            name= f'{nearest_line2.type} {int(math.degrees(nearest_line2.type_angle))}',
            radius=3,
            color=5
        )
        _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/parallel_or_perpendicular_{counter}.dxf')
        print('saved', f'parallel_or_perpendicular_{counter}.dxf')
            
        end_point_sets = []
        
        #DEBUG:
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace();
        
        # 2. Now find the end_points of each nearest_line:
        end_point_sets = get_end_points(
            nearest_line1=nearest_line1, nearest_line2=nearest_line2, entity_location=entity_location)

        # mapping sets to int
        end_point_sets[0] = set(map(lambda point: (int(point[0]), int(point[1])), end_point_sets[0]))
        end_point_sets[1] = set(map(lambda point: (int(point[0]), int(point[1])), end_point_sets[1]))
        
        left_end_points = list(end_point_sets[0])
        right_end_points = list(end_point_sets[1])
        
        # DEBUG
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1])
        for loc in (left_end_points + right_end_points):
            _msp.add_circle(loc, radius=1, dxfattribs={'color':3})
        __debug_location(
            msp=_msp,
            name='EL',
            point=entity_location,
            radius=1,
            color=4
        )
        _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/endpoints_{counter}.dxf')
        print('saved', f'endpoints_{counter}.dxf')

        
        
        end_points = match_both_end_points(
            left_end_points[0], left_end_points[1], right_end_points[0], right_end_points[1])
        
        # DEBUG:
        # for end_point in end_points
        
        return end_points
        
    
    def adjust_extended_lines(entity_location: float, graph: 'nx.Graph', extended_lines: List[tuple]):
        """This function adjusts the extended_lines from the entity.
        
        Procedure:
            1. loop on extended lines:
                for extended_line in extended_lines:
            2 check for the left side first:
                2.1 check the left point lies on which edge: (intersection.)
                left_edge = get_edge_for_point()
                    intersection
                        for edge in graph.edges:
                            return is_between(point, edge)
                2.2 check if any node if left_end_points are nodes of the edge:
                    is_left_end_point1_a_node = check if it is in any of the nodes of edge
                    is_left_end_point2_a_node = check if it is in any of the nodes of edge
                2.3 if both the points are node 
                    2.3.1 then simply remove the edge
                2.4 elif if one of the point is node:
                    break the line from edge partially using the function break edge into two using the node which is not on the edge.
                2.5 elif none of the node is forming the edge:
                    then make the deconstruct the line into sequence using the unary_union (shapely method):
                        Example:
                        Current Scenario:
                        A----(B)----(C)-----D, we have edges as (A-D), (B-C)
                        which means that edges B-C is overlapping upon the A-D.
                        we want a output like: edges: A-B, B-C, C-D
                        which will be fetched using the unary_union.
            3. Repeat the point 2 for the right end points.
            4. return
        Args:
            entity_location (float): [description]
            graph (nx.Graph): [description]
            extended_lines (List[tuple]): [description]

        Raises:
            ValueError: [description]
        """
        # DEBUG: Sorting the extended lines before:
        extended_lines[0] = list(extended_lines[0]); extended_lines[0].sort(); extended_lines[0] = tuple(extended_lines[0])
        extended_lines[1] = list(extended_lines[1]); extended_lines[1].sort(); extended_lines[1] = tuple(extended_lines[1])

        left_nodes = list(map(lambda extended_line: extended_line[0], extended_lines))
        right_nodes = list(map(lambda extended_line: extended_line[1], extended_lines))
                
        # FOR LEFT NODE:
        # 1. only choosing the first left node as if first node is found on an edge then most probably the second node will also be on the edge
        first_left_node, second_left_node = left_nodes[0], left_nodes[1]
        
        found_left_edge, both_nodes_lie_on_a_single_edge = False, True
        for edge in graph.edges():
            if is_between(point=first_left_node, line_start=edge[0], line_end=edge[1]) and is_between(point=second_left_node, line_start=edge[0], line_end=edge[1]):
                left_edge = edge
                found_left_edge = True
                break
        
        # Case where edge is not between both the nodes.
        if not found_left_edge:
            for edge in graph.edges():
                if is_between(point=first_left_node, line_start=edge[0], line_end=edge[1]) or is_between(point=second_left_node, line_start=edge[0], line_end=edge[1]):
                    left_edge = edge
                    both_nodes_lie_on_a_single_edge = False
                    break
        
        # 2.2 check if any node if left_end_points are nodes of the edge:
        #     is_left_end_point1_a_node = check if it is in any of the nodes of edge
        #     is_left_end_point2_a_node = check if it is in any of the nodes of edge
        is_left_end_point1_a_node = first_left_node in {left_edge[0], left_edge[1]}
        is_left_end_point2_a_node = second_left_node in {left_edge[0], left_edge[1]}
                
        # 2.3 if both the points are node 
        if is_left_end_point1_a_node and is_left_end_point2_a_node:
            # edge is to be removed:
            graph.remove_edge(left_edge[0], left_edge[1])
        # 2.4 elif if one of the point is node:
        elif is_left_end_point1_a_node or is_left_end_point2_a_node:
            node_to_be_broken = second_left_node if is_left_end_point1_a_node else first_left_node
            break_edge_into_two_edges(edge=left_edge, node=node_to_be_broken, graph=graph)
            # Now remove the edge for the left_end points:
            graph.remove_edge(first_left_node, second_left_node)
        # 2.5 None of the edge is a node of any other edge
        else:
            from shapely.geometry import LineString
            from shapely.ops import unary_union, linemerge
            lines = [
                LineString([first_left_node, second_left_node]),
                LineString([left_edge[0], left_edge[1]]),
            ]
            line_segments = unary_union(lines)
            
            # EXCEPTION HANDLING:
            if len(list(line_segments)) != 3:
                print("EXCEPTION OCCURED, LENGTH OF LINE SEGMENT IS NOT 3!")
                print(f'line_segments: {line_segments.wkt}')
                print({"first_left_node": first_left_node, "second_left_node": second_left_node, "left_edge": {left_edge}})
                raise ValueError("LineSegments cannot be segregated.")
            
            # Cleaning line segments:
            edges = []
            # TEST:
            merged_line = linemerge(list(line_segments))
            line = []
            # for coordinate in merged_line.coords:
            #     line.append(coordinate)
            #     if len(line) == 2:
            #         edges.append(tuple(line))
            #         line = line[1:]
            
            
            for line_segment in line_segments:
                coords = list(line_segment.coords)
                for coord in coords:
                    coord = tuple(map(int, coord))
                coords.sort()
                coords = tuple(coords)
                edges.append(coords)
            edges.sort()
            
            # DEBUG:
            _dwg = ezdxf.new()
            _msp = _dwg.modelspace()
            
            __debug_location(
                msp = _msp,
                point = find_mid_point(edges[0][0], edges[0][1]),
                name = 'E1',
                radius = 1,
                color=3
            )
            __debug_location(
                msp = _msp,
                point = find_mid_point(edges[1][0], edges[1][1]),
                name = 'E2',
                radius = 1,
                color=3
            )
            __debug_location(
                msp = _msp,
                point = find_mid_point(edges[2][0], edges[2][1]),
                name = 'E3',
                radius = 1,
                color=3
            )
            
            for edge in graph.edges:
                _msp.add_line(edge[0], edge[1])
                
            _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/multiple_edges_left_{counter}.dxf')
            print('saved', f'multiple_edges_{counter}.dxf')
            
            # Now remove the middle segment
            edges_to_be_added = (edges[0], edges[2])
            edges_to_be_removed = [edges[1]]
            
            graph.remove_edge(left_edge[0], left_edge[1])
            graph.add_edges_from(edges_to_be_added)


        # FOR RIGHT NODE:
        # 1. only choosing the first right node as if first node is found on an edge then most probably the second node will also be on the edge
        first_right_node, second_right_node = right_nodes[0], right_nodes[1]
        
        found_right_edge, both_nodes_lie_on_a_single_edge = False, True
        for edge in graph.edges():
            if is_between(point=first_right_node, line_start=edge[0], line_end=edge[1]) and is_between(point=second_right_node, line_start=edge[0], line_end=edge[1]):
                right_edge = edge
                found_right_edge = True
                break
            
        # Case where edge is not between both the nodes.
        if not found_right_edge:
            for edge in graph.edges():
                if is_between(point=first_right_node, line_start=edge[0], line_end=edge[1]) or is_between(point=second_right_node, line_start=edge[0], line_end=edge[1]):
                    right_edge = edge
                    both_nodes_lie_on_a_single_edge = False
                    break
            
        
        # 2.2 check if any node if right_end_points are nodes of the edge:
        #     is_right_end_point1_a_node = check if it is in any of the nodes of edge
        #     is_right_end_point2_a_node = check if it is in any of the nodes of edge
        is_right_end_point1_a_node = first_right_node in {right_edge[0], right_edge[1]}
        is_right_end_point2_a_node = second_right_node in {right_edge[0], right_edge[1]}
        
        # 2.3 if both the points are node 
        if is_right_end_point1_a_node and is_right_end_point2_a_node:
            # edge is to be removed:
            graph.remove_edge(right_edge[0], right_edge[1])
        # 2.4 elif if one of the point is node:
        elif is_right_end_point1_a_node or is_right_end_point2_a_node:
            node_to_be_broken = second_right_node if is_right_end_point1_a_node else first_right_node
            break_edge_into_two_edges(edge=right_edge, node=node_to_be_broken, graph=graph)
            # Now remove the edge for the right_end points:
            graph.remove_edge(first_right_node, second_right_node)
        # 2.5 None of the edge is a node of any other edge
        else:
            from shapely.geometry import LineString
            from shapely.ops import unary_union, linemerge
            lines = [
                LineString([first_right_node, second_right_node]),
                LineString([right_edge[0], right_edge[1]]),
            ]
            line_segments = unary_union(lines)
            
            # EXCEPTION HANDLING:
            if len(list(line_segments)) != 3:
                print("EXCEPTION OCCURED, LENGTH OF LINE SEGMENT IS NOT 3!")
                print(f'line_segments: {line_segments.wkt}')
                print({"first_right_node": first_right_node, "second_right_node": second_right_node, "right_edge": {right_edge}})
                raise ValueError("LineSegments cannot be segregated.")
            
            # Cleaning line segments:
            edges = []
            # TEST:
            merged_line = linemerge(list(line_segments))
            # line = []
            # for coordinate in merged_line.coords:
            #     line.append(coordinate)
            #     if len(line) == 2:
            #         edges.append(tuple(line))
            #         line = line[1:]
                    
            for line_segment in line_segments:
                coords = list(line_segment.coords)
                for coord in coords:
                    coord = tuple(map(int, coord))
                coords.sort()
                coords = tuple(coords)
                edges.append(coords)
            edges.sort()
            
            # DEBUG:
            _dwg = ezdxf.new()
            _msp = _dwg.modelspace()
            
            __debug_location(
                msp = _msp,
                point = find_mid_point(edges[0][0], edges[0][1]),
                name = 'E1',
                radius = 1,
                color=3
            )
            __debug_location(
                msp = _msp,
                point = find_mid_point(edges[1][0], edges[1][1]),
                name = 'E2',
                radius = 1,
                color=3
            )
            __debug_location(
                msp = _msp,
                point = find_mid_point(edges[2][0], edges[2][1]),
                name = 'E3',
                radius = 1,
                color=3
            )
            
            for edge in graph.edges:
                _msp.add_line(edge[0], edge[1])
                
            _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/multiple_edges_right_{counter}.dxf')
            print('saved', f'multiple_edges_{counter}.dxf')
            
            # Now remove the middle segment
            edges_to_be_added = (edges[0], edges[2])
            edges_to_be_removed = [edges[1]]
            
            graph.remove_edge(right_edge[0], right_edge[1])
            graph.add_edges_from(edges_to_be_added)

        # finally adding both the lines edges:
        graph.add_edges_from(extended_lines)
        
        # Adding data to the extended edges:
        for edge in extended_lines:
            graph[edge[0]][edge[1]]['entity'] = entity
        
        # DEBUG:
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace()
        __debug_location(
            msp= _msp,
            point= find_mid_point(left_edge[0], left_edge[1]),
            name='left_edge',
            radius=1,
            color=4,
            char_height=1
        )
        __debug_location(
            msp= _msp,
            point= find_mid_point(right_edge[0], right_edge[1]),
            name='right_edge',
            radius=1,
            color=4,
            char_height=1
        )
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1])
        _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/chosen_edges_{counter}.dxf')
        print('saved', f'chosen_edges_{counter}.dxf')
        
        return


    def get_entity_location_for_door_at_the_centre(nearest_line1: "CentreLine", nearest_line2: "CentreLine", entity_location: float) -> float:
        """This function gives a centrepoint (entity_location) for the door.
        Reason for this function:
            This function is required because the door's location (original entity_location) is not located at the center and this is
            the reason why the walls can not be extended untill and unless we adjust the entity_location.
        
        Procedure:
            1. Get angle from both nl1 and nl2 and label them as "parallel" or "perpendicular" with respect to the entity location:
                for nearest_line in (nearest_line1, nearest_line2):
                    closest_point = nearest_line.get_closest_point(entity_location)
                    distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.start_point
                    # angle between entity location and closest point
                    angle = find_angle(entity_location, closest_point, distant_point)
                    
                    nearest_line.type = PARALLEL if is_angle_is_180_or_0_degrees(angle) else PERPENDICULAR
                    nearest_line.type_angle = angle
                    
            2. Now we have to find the centre-point for three cases:
                2.1 Case1: Parallel, Parallel
                2.2 Case2: Parallel, Perpendicular
                2.3 Case3: Perpendicular, Perpendicular
                    door_centre_point = get_door_centre_point(nl1, nl2)
                
            3. Return door centre points


        Args:
            nearest_line1 (CentreLine): [description]
            nearest_line2 (CentreLine): [description]

        Raises:
            ValueError: [description]

        Returns:
            float: [description]
        """
        def get_door_centre_points_from_parallel_lines(nearest_line1, nearest_line2, entity_location):
            """This function finds the centre line if both the lines are PARALLEL.
            Procedure:
                1. Validate both the lines are parallel.
                2. Find closest_point1 and closest_point2
                3. Return mid_point(closest_point1, closest_point2)
            """
            # 1. Validate both the lines are parallel.
            if not (nearest_line1.type == PARALLEL and nearest_line2.type == PARALLEL):
                raise ValueError(f"Only parallel lines wrt to the entity location is allowed in the function.Instead got: 1:{nearest_line1.type}, 2:{nearest_line1.type}.")
                        
            # 2. Find closest_point1 and closest_point2
            closest_point1 = nearest_line1.get_closest_point(entity_location)
            closest_point2 = nearest_line2.get_closest_point(entity_location)
            
            # Return mid_point(closest_point1, closest_point2)
            return find_mid_point(closest_point1, closest_point2)
        
        def get_door_centre_points_from_mixed_lines(nearest_line1, nearest_line2, entity_location):
            """This function finds the centre line if one line is PARALLEL and one is PERPENDICULAR.
            Procedure:
                1. Validate the lines.
                2. Find parallel_line and perpendicular_line.
                3. find perpendicular point from the closest_point of parallel_line to perpendicular_line.
                4. Return mid_point(closest_point, perpendicular_point)
            """
            # 1. Validate the lines.
            if not {nearest_line1.type, nearest_line2.type} == {PARALLEL, PERPENDICULAR}:
                raise ValueError(f"Only parallel and perpendicular lines wrt to the entity location is allowed in the function.Instead got: 1:{nearest_line1.type}, 2:{nearest_line1.type}.")
            
            # 2. Find parallel_line and perpendicular_line.
            parallel_line = nearest_line1 if nearest_line1.type == PARALLEL else nearest_line2
            perpendicular_line = nearest_line1 if nearest_line1.type == PERPENDICULAR else nearest_line2
            
            # 3. find perpendicular point from the closest_point of parallel_line to perpendicular_line.
            closest_point_of_parallel_line = parallel_line.get_closest_point(entity_location)
            perpendicular_point = find_perpendicular_point(
                closest_point_of_parallel_line, perpendicular_line.start_point, perpendicular_line.end_point)
            
            # 4. Return mid_point(closest_point, perpendicular_point)
            return find_mid_point(closest_point_of_parallel_line, perpendicular_point)
        
        def get_door_centre_points_from_perpendicular_lines(nearest_line1, nearest_line2, entity_location):
            # 1. Validate both the lines are PERPENDICULAR.
            if not (nearest_line1.type == PERPENDICULAR and nearest_line2.type == PERPENDICULAR):
                raise ValueError(f"Only PERPENDICULAR lines wrt to the entity location is allowed in the function.Instead got: 1:{nearest_line1.type}, 2:{nearest_line1.type}.")
                        
            # 2. Find closest_point1 and closest_point2
            closest_point1 = nearest_line1.get_closest_point(entity_location)
            closest_point2 = nearest_line2.get_closest_point(entity_location)
            
            # Return mid_point(closest_point1, closest_point2)
            return find_mid_point(closest_point1, closest_point2)

        
        # TEST
        conversion_factor = {'mm': 1.0, 'inch': 0.0393701}
        DISTANCE_FOR_POINT_TO_FIND_ANGLE: float = 4 * conversion_factor['inch']
        # point_to_find_angle = directed_points_on_line(entity_location, math.pi/2, DISTANCE_FOR_POINT_TO_FIND_ANGLE)[0]
        point_to_find_angle = entity_location
        
        # 1. Get angle from both nl1 and nl2 and label them as "parallel" or "perpendicular" with respect to the entity location:
        for nearest_line in (nearest_line1, nearest_line2):
            closest_point = nearest_line.get_closest_point(point_to_find_angle)
            distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.end_point
            # angle between entity location and closest point
            angle = find_angle(point_to_find_angle, closest_point, distant_point)
            
            nearest_line.type = PARALLEL if is_angle_is_180_or_0_degrees(angle, buffer=0.4) else PERPENDICULAR
            nearest_line.type_angle = angle
            
            nearest_line.__closest_point = closest_point
            nearest_line.__distant_point = distant_point
            
        # DEBUG:
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace()
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1])
            
        __debug_location(
            msp = _msp, 
            point = point_to_find_angle,
            name= f'PTFA: {int(point_to_find_angle[0]), int(point_to_find_angle[1])}',
            radius=1,
            color=3
        )

        __debug_location(
            msp = _msp, 
            point = find_mid_point(nearest_line1.start_point, nearest_line1.end_point),
            name= f'{nearest_line1.type} {int(math.degrees(nearest_line1.type_angle))}',
            radius=3,
            color=5
        )
        
        
        __debug_location(
            msp = _msp, 
            point = nearest_line1.__closest_point,
            name= f'CP: {str(nearest_line1.__closest_point)}',
            radius=1,
            color=2
        )
        __debug_location(
            msp = _msp, 
            point = nearest_line1.__distant_point,
            name= f'DP: {str(nearest_line1.__distant_point)}',
            radius=1,
            color=2
        )
        
        __debug_location(
            msp = _msp, 
            point = find_mid_point(nearest_line2.start_point, nearest_line2.end_point),
            name= f'{nearest_line2.type} {int(math.degrees(nearest_line2.type_angle))}',
            radius=3,
            color=5
        )
        __debug_location(
            msp = _msp, 
            point = nearest_line2.__closest_point,
            name= f'CP: {str(nearest_line2.__closest_point)}',
            radius=1,
            color=2
        )
        __debug_location(
            msp = _msp, 
            point = nearest_line2.__distant_point,
            name= f'DP: {str(nearest_line2.__distant_point)}',
            radius=1,
            color=2
        )
        
        
        _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/DOOR_parallel_or_perpendicular_{counter}.dxf')
        print('saved', f'DOOR_parallel_or_perpendicular_{counter}.dxf')
        extra_data[counter] = {
            'nl1': f'{nearest_line1.type + str(int(math.degrees(nearest_line1.type_angle)))}',
            'nl2': f'{nearest_line2.type + str(int(math.degrees(nearest_line2.type_angle)))}',
        }

            
        # Fill wall_counter dict: (used to keep the count of no of parallel or perpendicular walls.)
        wall_counter_dict = OrderedDict.fromkeys((PARALLEL, PERPENDICULAR), value=0)
        for nearest_line in (nearest_line1, nearest_line2):
            wall_counter_dict[nearest_line.type] += 1
                        
        door_centre_point_function_mapper = {
            ((PARALLEL, 2), (PERPENDICULAR, 0)): get_door_centre_points_from_parallel_lines,
            ((PARALLEL, 1), (PERPENDICULAR, 1)): get_door_centre_points_from_mixed_lines,
            ((PARALLEL, 0), (PERPENDICULAR, 2)): get_door_centre_points_from_perpendicular_lines,
        }
        
        centre_point_function = door_centre_point_function_mapper[tuple(sorted(wall_counter_dict.items()))]
        
        door_centre_point = centre_point_function(
            nearest_line1=nearest_line1,
            nearest_line2=nearest_line2,
            entity_location=entity_location
        )
        
        return door_centre_point

        
    # 0. Preprocessing
    preprocess_module(graph=graph, *args, **kwargs)
    
    # 1. Do some exception handling to check the type of the entity is "door" or "window".
    ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED = ('door', 'window')
    if not entity['type'] in ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED:
        raise AttributeError(
            f'Only entities with types in {ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED} can be extended.')
        
    # 2. Get entity location:
    entity_location = entity["location"]
    entity_category = entity["category"]

    # 3. Get nearest centre lines to that entity:
    nearest_line1, nearest_line2 = get_nearest_centre_lines_from_a_point(
                point = entity_location, centre_lines = centre_lines, entity_location= entity_location)
    
    # DEBUG:
    print('Got nearest centre lines')
    
    # 4. Check if the entity is a "door", if it is then modify the entity_location
    if entity["type"] == "door":
        entity_location = get_entity_location_for_door_at_the_centre(nearest_line1, nearest_line2, entity_location)
        if entity_location is None:
            raise ValueError(f"entity_location cannot be None for door: {entity}")
        print('Changed entity_location for the door object.')
        
    # 5. For the first two nearest lines, extend the wall:
    extended_lines = get_extended_wall_lines_with_nearest_lines(
        entity_location, graph, nearest_line1, nearest_line2, entity_category=entity_category)
    print('got extended lines.', extended_lines)
    
    print('adjusting graph: ', len(graph.edges))
    # 6. Adjust the extended lines on the graph:
    adjust_extended_lines(graph=graph, extended_lines=extended_lines, entity_location=entity_location)
    print('adjusted graph', len(graph.edges))
    return


# Now Finding area of the extended edges:
def get_area_from_the_room_texts(msp, graph: 'nx.Graph', ROOM_TEXT_LAYER: str = 'PP-ROOM Text') -> dict:
    """This function returns the dict containing information about the Rooms and areas.
    NOTE: This function assumes that the graph contains all the nodes that are 2-degree.
    
    Procedure:
        1. Fetch the rooms.
            rooms = get_rooms(msp, ROOM_LAYER)
        1.1 Initialize the meta data:
            rooms_information = {}
        2. For each room:
            for room in rooms:
        2.1. Fetch the room-text coordinates
            room_coordinate = get_room_coordinates(room)
        2.2 Find the nearest lines (from the graph) from the room coordinates.
            nearest_lines = get_nearest_lines_from_a_point(point=room_coordinate, lines=graph.edges)
        2.3 Fetch the first nearest line:
            nearest_line = nearest_lines[0]
        2.4 Get the graph component from that contains that nearest-line:
            graph_component = get_graph_component_containing_edge(edge= nearest_line, graph= graph)
        2.5 Check if the graph component is closed:
            if graph_component.has_cycle():
                2.5.1  Fetch The room_area:
                    room_area = get_area_of_polygon(polygon=graph_component.edges)
                2.5.2 Populate Room information
                    room_information[room] = get_room_information(room)
        2.6 Else: print(Room {room.number} is not open.)
        3. return room_information          

    Args:
        graph (nx.Graph)
        ROOM_TEXT_LAYER (str, optional): The layer in which texts of the rooms are stored. Defaults to 'PP-ROOM Text'.

    Returns:
        dict: [description]
    """
    def get_rooms(msp, ROOM_TEXT_LAYER: str):
        def get_mtext_rooms(msp, ROOM_TEXT_LAYER: str) -> list:
            rooms = []
            mtext_rooms = msp.query(f'MTEXT[layer=="{ROOM_TEXT_LAYER}"]')
            rooms = list(
                map(lambda mtext_room: {'room_name': mtext_room.plain_text(), 'room_location': mtext_room.dxf.insert}, mtext_rooms))
            return rooms

        def get_text_rooms(msp):
            pass
        
        rooms = get_mtext_rooms(msp, ROOM_TEXT_LAYER)
        # TODO: Need to extend the rooms for the rooms in the text layer.
        return rooms

    def get_room_coordinates(room):
        return room['room_location']
    
    def get_ordered_edges(graph_component):
        from networkx.algorithms.traversal.depth_first_search import dfs_edges
        dfs_traversal = list(dfs_edges(graph_component))
        first_node, last_node = dfs_traversal[0][0], dfs_traversal[-1][1]
        dfs_traversal.append((first_node, last_node))
        return dfs_traversal
    
    def get_graph_component_containing_edge(edge: tuple, graph: nx.Graph) -> nx.Graph:
        """This function returns a copy of subgraph from the original graph which contains the edge given the function."""
        graph_component_set_containing_edge = list(filter(lambda component: graph.subgraph(
            component).has_edge(edge[0], edge[1]), nx.connected_components(graph)))[0]
        graph_component = graph.subgraph(
            graph_component_set_containing_edge).copy()
        return graph_component
    
    def has_cycle(graph_component: nx.Graph) -> bool:
        """This function detects if the graph has cycle present in it or not."""
        return len(nx.find_cycle(graph_component)) > 0

    def get_area_of_polygon(graph_component):
        ordered_edges = get_ordered_edges(graph_component)
        polygon_input_points = pointslist_from_lines(ordered_edges)
        polygon_object = define_polygons(polygon_input_points)
        area = find_polygon_area(polygon_object)
        return area
    
    def get_ordered_points_from_graph_component(graph_component: nx.Graph):
        from shapely.ops import polygonize
        TOLERANCE_FACTOR: float = 0.05
        ordered_edges = get_ordered_edges(graph_component)
        polygon_from_ordered_edges = list(polygonize(ordered_edges))[0]
        simplified_polygon = polygon_from_ordered_edges.simplify(TOLERANCE_FACTOR)
        polygon_coordinates = list(simplified_polygon.exterior.coords)
        return polygon_coordinates

    def get_room_information(room, room_area: float, graph_component: nx.Graph = None):
        room_information = {
            'room': room,
            'area': room_area,
            'graph_component': graph_component,
            'ordered_points': get_ordered_points_from_graph_component(graph_component)
        }
        return room_information

    # 1. Fetch the rooms.
    rooms = get_rooms(msp, ROOM_TEXT_LAYER)
    rooms_information = []
    
    # 2. For each room:
    for room in rooms:
        # 2.1. Fetch the room-text coordinates
        room_coordinate = get_room_coordinates(room)
        # 2.2 Find the nearest lines (from the graph) from the room coordinates.
        nearest_lines = get_nearest_lines_from_a_point(
            point=room_coordinate, lines=list(graph.edges))
        # 2.3 Fetch the first nearest line:
        nearest_line = nearest_lines[0]
        # 2.4 Get the graph component from that contains that nearest-line:
        graph_component = get_graph_component_containing_edge(
            edge=nearest_line, graph=graph)
        
        # 2.5 Check if the graph component is closed:
        try:
            if has_cycle(graph_component):
                # 2.5.1  Fetch The room_area:
                room_area = get_area_of_polygon(graph_component)
                # 2.5.2 Populate Room information
                room_information = get_room_information(room, room_area, graph_component)
                rooms_information.append(room_information) 
            # 2.6 Else: print(Room {room.number} is not open.)
        except:
            print(f'Room {room["room_name"]} is not open.')

    return rooms_information


def plot_room_areas(rooms_information: List[dict], msp, dwg, doors, windows):
    for room_index, room in enumerate(rooms_information):
        location = room['room']['room_location']
        area = room['area']
        room_name = room['room']['room_name']
        ordered_points = room['ordered_points']
        
        # Make Polyline across rooms:
        room_polyline_layer = f'PP-ROOM BOUNDRY {room_index}'
        room_polyline = msp.add_lwpolyline(ordered_points, dxfattribs = {'layer': room_polyline_layer})
        
        # add hatch for the polyline:
        room_hatch_layer = f'PP-ROOM HATCH {room_index}'
        hatch = msp.add_hatch(color=2, dxfattribs={'layer': room_hatch_layer})  # by default a solid fill hatch with fill color=7 (white/black)
        hatch.paths.add_polyline_path(ordered_points)
        
        # label the ordered_points:
        wall_label = 'A'
        for i in range(len(ordered_points) - 1):
            wall = (ordered_points[i], ordered_points[i+1])
            location_to_label = find_mid_point(wall[0], wall[1])
            label_text = msp.add_mtext(wall_label, dxfattribs={'layer': room_polyline_layer})
            label_text.set_location(location_to_label)
            
            # incrementing th wall_label now:
            wall_label = chr(ord(wall_label) + 1)

        
        # DEBUG
        __debug_location(
            msp=msp, point=location, name=f'{room_name}\n{area}', radius=0.5, color=4, char_height=3, layer='PP ROOM-AREA'
        )
        
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace()
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1], dxfattribs={'layer': 'graph_lines'})
            
        for edge in room['graph_component'].edges:
            _msp.add_line(edge[0], edge[1], dxfattribs={'layer': 'GRAPH-COMPONENT', 'color': 2})
        __debug_location(
            msp=_msp, point=location, name=f'{room_name}\n{area}', radius=0.5, color=4, char_height=3, layer='PP ROOM-AREA'
        )
        _dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/graph_component_{room_index}.dxf')
        print('saved', f'dxfFilesOut/{input_key}/debug_dxf/extended_wall_lines/graph_component_{room_index}.dxf')

    # Removing unwanted layers (for debug)
    try:
        entities = msp.query("")
        dwg.layers.remove('CenterLines')
        print(f'Removed centrelines')
    except:
        pass
    try:
        dwg.layers.remove('debug')
        print(f'Removed debug')
    except:
        pass
    
    # labelling doors and windows:
    for door in doors:
        door_name = door['display_name']
        door_location = door['location']
        door_text = msp.add_mtext(door_name, dxfattribs = {'layer': 'PP-DOOR LABEL'})
        door_text.set_location(door_location)
        
    for window in windows:
        window_name = window['display_name']
        window_location = window['location']
        window_text = msp.add_mtext(window_name, dxfattribs = {'layer': 'PP-WINDOW LABEL'})
        window_text.set_location(window_location)
    print('Windows and Doors labelled')    
    
    
    dwg.saveas(f'dxfFilesOut/{input_key}/debug_dxf/rooms_area.dxf')
    print('SUCCESS in saving, ', f'dxfFilesOut/{input_key}/debug_dxf/rooms_area.dxf')

# plot_room_areas(rooms_information)
