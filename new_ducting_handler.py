from typing import List, Dict
import networkx as nx
import json
import matplotlib.pyplot as plt
import math
from pillarplus.math import is_inverted, find_angle, find_rotation, directed_points_on_line, find_perpendicular_slope_angle,find_perpendicular_point,is_between
import ezdxf
from ezdxf.math import Vector, Vec2
from pillarplus.blocks import place_block_at_location
import re
from ezdxf.addons import Importer
import os
import pprint

# Constants:
SERVICE_NAME: str = 'ducting'


# Containers
class Ducting:
    def __init__(self, number):
        self.number = number
        
        
def __debug_location(point, name: str = 'debug', radius = 2, color:int = 2):
    msp.add_circle(point, radius, dxfattribs={'color': color})
    msp.add_mtext(name).set_location(point)


def get_json_object():
    this_dir = os.path.dirname(__file__) + '/'

    
    input_file_name = 'updated_identification.json'
    with open(this_dir + input_file_name) as f:
        data = json.load(f)
        print(f'Json File: {input_file_name} read success! at {this_dir}')
    return data


def get_joints_dict(json) -> dict:
    """Returns a joints dict with its key as joints numbers.

    Args:
        json (dict): Read from identification.json

    Returns:
        dict: Returns a joints dict with its key as joints numbers.
    """
    joints_dict = {}
    for joint in json['joints']:
        if joint['service'] == 'ducting':
            joints_dict[joint['number']] = joint
    return joints_dict

def get_entities_dict(data) -> dict:
    """This functions returns an entities dict

    Args:
        data (dict): JSON read data from identification.json

    Returns:
        dict: Entities dict
    """
    entities_dict = {}
    for entity in data['entities']:
        if entity['service'] == 'ducting':
            entities_dict[entity['number']] = entity
    return entities_dict


def get_connections(data: dict) -> list:
    """This functions returns all the connections of service 'ducting'.

    Args:
        data (dict): JSON file read object from identification.json

    Returns:
        list: Returns all the connections in a list.
    """
    connections = []
    for connection in data['connections']:
        if connection['service'] == 'ducting':
            connections.append(connection)
    return connections


def get_joint_defaults(data: dict) -> dict:
    """This function returns joint_defaults from JSON file.

    Args:
        data (dict): JSON read data from identification.json

    Returns:
        dict: joint_defaults dicts.
    """
    joint_defaults = data['joint_defaults']
    custom_joint_defaults = {}
    for joint_default in joint_defaults:
        key = joint_default['type'] + ('_mirror' if joint_default['mirror'] else '')
        value = joint_default
        custom_joint_defaults[key] = value
    return custom_joint_defaults


def to_directed_dfs(graph, head, visited, directed_graph, reverse):
    if visited[head] != 0:
        return None
    visited[head] = 1
    for i in graph.adj[head]:
        j = to_directed_dfs(graph, i, visited, directed_graph, reverse)
        if j != None:
            directed_graph.add_node(head, **graph.nodes[head])
            directed_graph.add_node(j, **graph.nodes[j])
            if reverse:
                directed_graph.add_edge(j, head, **graph[j][head])
            else:
                directed_graph.add_edge(head, j, **graph[j][head])
    return head

def dfs_to_shift_locations(graph,head):

    current_node = head
    current_node_obj = graph.nodes[current_node]
    location = current_node_obj['location']
    parent_list = list(graph.predecessors(current_node))
    parent_node = parent_list[0] if len(parent_list) != 0 else None
    child_nodes = list(graph.adj[current_node])
    child_node = child_nodes[0] if len(child_nodes) != 0 else None
    child_edge_obj = graph[current_node][child_node] if child_node != None else None

    if parent_node != None:
        parent_node_obj = graph.nodes[parent_node]
        parent_edge_obj = graph[parent_node][current_node]
        parent_width = float(parent_edge_obj['size'].split('x')[0])
        child_width = float(child_edge_obj['size'].split('x')[0]) if child_edge_obj != None else 40
        parent_rotation = find_rotation(parent_node_obj['location'],location)
        angle_per = find_perpendicular_slope_angle(parent_node_obj['location'],location)
        parent_vector = parent_node_obj['vector']

        shift_amount, shift_direction = parent_vector.magnitude,parent_vector.angle
        current_node_obj['shifted_location'] = directed_points_on_line(location,shift_direction,shift_amount)[0]
        current_node_obj['vector'] = parent_vector
        current_node_obj['connection_point'] = current_node_obj['shifted_location']
        
        if current_node_obj['type'] == 'reducer':

            current_node_obj['taper'] = "120"
            if current_node_obj['taper'] != None:
                taper_type = current_node_obj['taper']
                int_part = taper_type.split('.')[0]

                if re.sub("[^0-9]","",int_part) != '':
                    taper_angle = float(taper_type)*(math.pi/180)
                    check_shift = (parent_width-child_width) / math.cos(30 * (math.pi / 180))
                    
                    #Which taper slant UP or DOWN ?
                    point1 = directed_points_on_line(current_node_obj['shifted_location'],angle_per,parent_width/2)[0]
                    msp.add_circle(point1, 4, dxfattribs = {'color': 4}); msp.add_mtext('point1').set_location(point1)
                    point2 = directed_points_on_line(current_node_obj['shifted_location'],angle_per,parent_width/2)[1]
                    msp.add_circle(point2, 4, dxfattribs = {'color': 4}); msp.add_mtext('point2').set_location(point2)
                    rotation = find_rotation(location,point2)*(math.pi/180)

                    p1 = directed_points_on_line(point1,taper_angle,check_shift)[0] #slant end
                    # msp.add_circle(p1, 10); msp.add_mtext('p1').set_location(p1)
                    p2 = directed_points_on_line(point2,taper_angle,check_shift)[0] #slant end
                    # msp.add_circle(p2, 10); msp.add_mtext('p2').set_location(p2)

                    #checking whether Point1 is desired or Point2 is desired.
                    per_point1 = find_perpendicular_point(p1, point1, point2)
                    # msp.add_circle(p1, 5); msp.add_mtext('per_point1').set_location(per_point1)
                    per_point2 = find_perpendicular_point(p2, point1, point2)
                    # msp.add_circle(p1, 5); msp.add_mtext('per_point2').set_location(per_point2)
                    # __debug_location(per_point1, f'per_point1\n{per_point1}', 1)
                    # __debug_location(per_point1, f'per_point2\n{per_point2}', 1)
                    
                    
                    print(f'per_point1: {per_point1}', f'per_point2: {per_point2}')

                    if is_between(per_point1,point1,point2):
                        msp.add_mtext('Chosen Per-Point1').set_location(per_point1)
                        slant_start_point = point1
                        shift_direction = find_rotation(point1,per_point1)
                        vector = ezdxf.math.Vector(per_point1)-ezdxf.math.Vector(point1)
                        current_node_obj['vector'] = parent_vector+vector
                        vec = current_node_obj['vector']
                        # msp.add_circle(per_point1, 10)
                        #msp.add_circle(per_point1,7,dxfattribs={"color":1})
                        
                        current_node_obj['connection_point'] = directed_points_on_line(current_node_obj['shifted_location'],vec.angle,vec.magnitude / 2)[0]
                        print('1')

                    elif is_between(per_point2,point1,point2):
                        # msp.add_mtext('Chosen Per-Point2').set_location(per_point2)
                        print('Chosen Per-point2')
                        print(dict(child_width=child_width, parent_width=parent_width))
                        # msp.add_circle(per_point2, 10)
                        slant_start_point = point2
                        shift_direction = find_rotation(point2,per_point2)
                        
                        #msp.add_circle(point2,7,dxfattribs={"color":4})
                        #msp.add_circle(per_point2,3,dxfattribs={"color":92})
                        vector =  Vector(per_point2) - Vector(point2) #ezdxf.math.Vector(per_point2)-ezdxf.math.Vector(point2)
                        current_node_obj['vector'] = parent_vector+vector
                        vec = current_node_obj['vector']
                        print(vec.magnitude,"MAGNITUDE",vec.magnitude/2)
                        current_node_obj['connection_point'] = directed_points_on_line(current_node_obj['location'],vec.angle,vec.magnitude)[0]
                        print('2')
                        pprint.pprint({'L': current_node_obj['location'], 'SL': current_node_obj['shifted_location'], 'CP': current_node_obj['connection_point']})
                        
                    else:
                        print("No Between Points")

            else:
                print('Taper with reducer is NULL')					


        # FOR DEBUG of L, SL and CP:
        __debug_location(point = current_node_obj['location'], name = "L", radius = 1, color = 1)
        __debug_location(point = current_node_obj['shifted_location'], name = "SL", radius = 1, color = 3)
        __debug_location(point = current_node_obj['connection_point'], name = "CP", radius = 1, color = 4)        
    else:
        print("NONE PARENT")
        current_node_obj['vector'] = ezdxf.math.Vector(0,0,0)
        current_node_obj['shifted_location'] = current_node_obj['location']
        current_node_obj['connection_point'] = current_node_obj['location']


    for node in graph.adj[head]:
        dfs_to_shift_locations(graph,node)











        











def get_directed_graph(graph, priority_list, reverse=False) -> nx.DiGraph:
    '''
    '''
    visited = {}
    directed_graph = nx.DiGraph()
    for i in graph.nodes:
        visited[i] = visited.get(i, 0)
    for priority_list_item in priority_list:
        for i in graph.nodes:
            if graph.nodes[i]['type'] == priority_list_item and visited[i] == 0:
                to_directed_dfs(graph, i, visited, directed_graph, reverse)
    for i in graph.nodes:
        if visited[i] == 0:
            to_directed_dfs(graph, i, visited, directed_graph, reverse)
    return directed_graph


def create_hash(type, number):
    """
    returns hash values for nodes of the graph
    """
    if type == 'Entity':
        return 'E'+str(number)
    elif type == 'Joint':
        return 'J'+str(number)
    else:
        return str(number)


def get_graph(connections, joints_dict, entities_dict=None) -> nx.Graph:

    """
    Creates a directed graph from connections and joints/etites read from json. Store there properties as atrributes in dictionary of nodes and connections

    Parameters:
    connection - JSON fromat connections
    joints_dict - joints dictionary with key as joint_number and value as JSON joints
    entities_dict - joints dictionary with key as entity_number and value as JSON entities

    Returns:
    networkx directed graph of connections and joints

    Dependencies:
    uses create hash function to make hashable nodes as they can be of either joints or entities type

    """

    graph = nx.Graph()
    for connection in connections:
     
        source_number = connection['source_number']
        target_number = connection['target_number']
        source_type = connection['source_type']
        target_type = connection['target_type']
        source_dict = entities_dict[source_number] if source_type=='Entity' else joints_dict[source_number]
        target_dict = entities_dict[target_number] if target_type=='Entity' else joints_dict[target_number]

        graph.add_node(create_hash(source_type,source_number), **source_dict)
        graph.add_node(create_hash(target_type,target_number), **target_dict)
        graph.add_edge(create_hash(source_type,source_number), create_hash(target_type,target_number), **connection)

    return graph

def assign_side_trim_end_trim(graph: nx.DiGraph, joint_defaults: dict):
    """This function assigns start_trim and end_trim to all the edges of the graphs.

    Args:
        graph (nx.DiGraph): A directed graph created by the function 'get_directed_graph'.
    """
    mirror = '_mirror'
    DEFAULT_SIZE = 75
    
    for node in graph.nodes():
        in_degree = graph.in_degree(node)
        # Validating in_degree:
        if in_degree > 1:
            raise ValueError(f'Exception: "in_degree" cannot be more than one in ducting. Exception occured in node: {node}')
        
        out_degree = graph.out_degree(node)
        
        if graph.nodes[node]['type'] in ('bend', 'elbow'):
             
            # finding parent and child nodes
            parent_node = list(graph.predecessors(node))[0]
            child_node = list(graph.successors(node))[0]
            
            # finding parent and child edges
            parent_edge = graph[parent_node][node]
            child_edge = graph[node][child_node]
            
            # Making key for joint default
            #graph.nodes[node]['mirror'] = graph.nodes[node].get('mirror',False)
            joint_default_key = graph.nodes[node]['type'] + (mirror if graph.nodes[node]['mirror'] else '')
            # Fetching joint default from key
            joint_default = joint_defaults[joint_default_key]
            intrim = joint_default.get('intrim', 0)
            outtrim = joint_default.get('outtrim', 0)
            
            # Now finding the start and out trims of each edges
            width = int(parent_edge['size'].split('x')[0])*FACTOR
            parent_edge['end_trim'] = intrim*(width/75)
            child_edge['start_trim'] = outtrim*(width/75)
            
        elif graph.nodes[node]['type'] == 'reducer':
            # finding parent and child nodes
            parent_node = list(graph.predecessors(node))[0]
            child_node = list(graph.successors(node))[0]
            
            # finding parent and child edges
            parent_edge = graph[parent_node][node]
            child_edge = graph[node][child_node]
            
            # Calculating the intrim and outtrim
            width_of_parent_edge = int(parent_edge['size'].split('x')[0])*FACTOR
            width_of_child_edge = int(child_edge['size'].split('x')[0])*FACTOR
            width_of_reducer = (width_of_parent_edge-width_of_child_edge)/2
            parent_edge['end_trim'] = 0
            child_edge['start_trim'] = width_of_reducer/2
            
            
        elif graph.nodes[node]['type'] == 't':
            # finding parent and child nodes
            parent_node = list(graph.predecessors(node))[0]
            child_nodes = list(graph.successors(node))
            
            # finding parent and child edges
            parent_edge = graph[parent_node][node]
            
            point = graph.nodes[node]['location']
            from_point = graph.nodes[parent_node]['location']
            
            # Find on which node we need to attach collar
            collar_node = None
            for child_node in child_nodes:
                to_point = graph.nodes[child_node]['location']
                angle = find_angle(from_point, point, to_point)
                if (math.pi/2 - 0.1 < angle < math.pi/2 + 0.1) or (3*math.pi/2 - 0.1 < angle < 3*math.pi/2 + 0.1):
                    collar_node = child_node
                    break
                
            # Now attach intrim and outtrim of collar
            child_edge = graph[node][collar_node]
            
            
            outtrim = float(parent_edge['size'].split('x')[0])*FACTOR
            
            # Now finding the start and out trims of each edges
            parent_edge['end_trim'] = 0
            child_edge['start_trim'] = outtrim
            
        elif graph.nodes[node]['type'] == 'special t':
            pass
        
        elif graph.nodes[node]['type'] == 'cross':
            # finding parent and child nodes
            parent_node = list(graph.predecessors(node))[0]
            child_nodes = list(graph.successors(node))
            
            # finding parent and child edges
            parent_edge = graph[parent_node][node]
            
            point = graph.nodes[node]['location']
            from_point = graph.nodes[parent_node]['location']

            # Fetching collar nodes
            collar_nodes = []
            for child_node in child_nodes:
                to_point = graph.nodes[child_node]['location']
                angle = find_angle(from_point, point, to_point)
                if (math.pi/2 - 0.1 < angle < math.pi/2 + 0.1) or (3*math.pi/2 - 0.1 < angle < 3*math.pi/2 + 0.1):
                    collar_nodes.append(child_node)
                
            # Collar nodes should be exactly two otherwise raising exception for this.
            if len(collar_nodes) != 2:
                raise ValueError(f'Exception: Their should be two collar nodes in three-way duct for proper assignment of start trim and end trim. Exception occured for node: {graph.nodes[node]}.')
            
            # Marking end_trim
            parent_edge['end_trim'] = 0
            
            
            outtrim = float(parent_edge['size'].split('x')[0])*FACTOR

            # Finding child_edges and modifying the outtrim if they are perpendicular 
            for child_node in collar_nodes:
                to_point = graph.nodes[child_node]['location']
                angle = find_angle(from_point, point, to_point)
                 
                if (math.pi/2 - 0.1 <= angle <= math.pi/2 + 0.1) or (3*math.pi/2 - 0.1 <= angle <= 3*math.pi/2 + 0.1):
                    child_edge = graph[node][child_node]
                    child_edge['start_trim'] = 1.5*outtrim
                     
                else:
                    child_edge['start_trim'] = 0


def update_graph_properties(graph, joint_defaults):
    """The function is used to update the graph properties for ease in drawing the ducting.
    This functions is used to update the following properties: 'size', 'rotation', 'type' and 'mirror', 'start_trim' and 'end_trim'.

    Args:
        graph (nx.DiGraph): [description]
        joint_defaults (dict): [description]
    """
    mirror = '_mirror'
    DEFAULT_SIZE = 75
     
    # Traversing the nodes to decide the type of joints:
    for node in graph.nodes:
        print(type(graph))
        
        in_degree = graph.in_degree(node)
        # Validating in_degree:
         
        if in_degree > 1:
            raise ValueError(f'Exception: "in_degree" cannot be more than one in ducting. Exception occured in node: {node}')
        

        out_degree = graph.out_degree(node)

         
        graph.nodes[node]['mirror'] = False
        if graph.nodes[node]['type'] is None:
            if in_degree == 1 and out_degree == 1:
                # finding parent and child nodes
                 
                parent_node = list(graph.predecessors(node))[0]
                child_node = list(graph.successors(node))[0]
                
                # finding parent and child edges
                parent_edge = graph[parent_node][node]
                child_edge = graph[node][child_node]
                
                # Checking if it is a mirror or not
                point = graph.nodes[node]['location']
                from_point = graph.nodes[parent_node]['location']
                to_point = graph.nodes[child_node]['location']
                 
                is_mirror = is_inverted(point, from_point, to_point)
                graph.nodes[node]['mirror'] =  is_mirror

                # Finding angle in between the three points
                angle = find_angle(from_point, point, to_point)
                if math.pi/2 - 0.1 <= angle <= math.pi/2 + 0.1 or 3*math.pi/2 - 0.1 <= angle <= 3*math.pi/2 + 0.1:
                    print(angle*(180/math.pi),'BEND ANGLE')
                    graph.nodes[node]['type'] = 'bend'
                else:
                    print(angle*(180/math.pi),"ELBOW ANGLE")
                    graph.nodes[node]['type'] = 'elbow'
                
                graph.nodes[node]['rotation'] = find_rotation(from_point, point)
                graph.nodes[node]['size'] = parent_edge.get('size', DEFAULT_SIZE)
                
            elif in_degree == 1 and out_degree == 2:
                # finding parent and child nodes
                parent_node = list(graph.predecessors(node))[0]
                child_nodes = list(graph.successors(node))
                
                # finding parent and child edges
                parent_edge = graph[parent_node][node]
                child_edges = [graph[node][child_node] for child_node in child_nodes]
                
                # This case will never be MIRROR.
                graph.nodes[node]['mirror'] = False
                
                # Getting points of child, parent and self nodes:
                point = graph.nodes[node]['location']
                from_point = graph.nodes[parent_node]['location']
                
                # Naming the childs
                one_eighty_child_found = False
                one_eighty_child = None
                to_point = graph.nodes[child_nodes[0]]['location']
                angle1 = find_angle(from_point, point, to_point)
                first_child = child_nodes[0]
                
                if math.pi - 0.1 < angle1 < math.pi + 0.1:
                    one_eighty_child_found = True
                    one_eighty_child = first_child
                    graph.nodes[node]['type'] = 't'
                
                other_child = child_nodes[1]
                to_point = graph.nodes[child_nodes[0]]['location']
                angle2 = find_angle(from_point, point, to_point)
                
                if math.pi - 0.1 < angle2 < math.pi + 0.1:
                    one_eighty_child_found = True
                    one_eighty_child = other_child
                    graph.nodes[node]['type'] = 't'

                if not one_eighty_child_found:
                    graph.nodes[node]['type'] = 'special t'

            elif in_degree == 1 and out_degree == 3:
                # finding parent and child nodes
                parent_node = list(graph.predecessors(node))[0]
                child_nodes = list(graph.successors(node))
                
                # finding parent and child edges
                parent_edge = graph[parent_node][node]
                child_edges = [graph[node][child_node] for child_node in child_nodes]
                
                # This case will never be MIRROR.
                graph.nodes[node]['mirror'] = False
                
                # Getting points of child, parent and self nodes:
                point = graph.nodes[node]['location']
                from_point = graph.nodes[parent_node]['location']

                graph.nodes[node]['type'] = 'cross'
                
                
        
        # Updating intrims and outtrims of graph also
        assign_side_trim_end_trim(graph, joint_defaults)

        for node in graph.nodes:
            if graph.nodes[node]['type'] == 'CS unit':
                dfs_to_shift_locations(graph,node)
                break
        


def clean_other_json_properties(json):
    pass


def draw_graph(directed_graph):
    plt.figure(figsize =(10,10))
    nx.draw_networkx(directed_graph)
    plt.axis('off')
    plt.tight_layout();
    plt.savefig('graph_image.jpg')

def draw_bend():
    pass
def draw_reducer():
    pass
def draw_elbow():
    pass
def draw_t():
    pass
def draw_special_t():
    pass
def draw_cross():
    pass

def get_collar_points(target_obj,child_obj,child_edge_obj,connection_rotation,width):
                
    per_angle = find_rotation(target_obj['connection_point'],child_obj['shifted_location'])*(math.pi/180)
    child_edge_width = int(child_edge_obj['size'].split('x')[0])
    collar_mid_point = directed_points_on_line(target_obj['shifted_location'],per_angle,width/2)[0]
    shift = 30*FACTOR
    collar_side_2_back = directed_points_on_line(collar_mid_point,connection_rotation,child_edge_width/2+shift)[0]
    between_point = directed_points_on_line(collar_mid_point,connection_rotation,child_edge_width/2)[0]
    collar_side_1_back = directed_points_on_line(collar_mid_point,connection_rotation,child_edge_width/2)[1]

    collar_height = width #child_edge_obj['start_trim'] #FACTOR
    print(width,"COLLAR HEIGHT",child_edge_obj['start_trim'])
    s,e = target_obj,child_obj
    child_edge_rotation = find_rotation(s['connection_point'],e['shifted_location'])*(math.pi/180)
    collar_side_1_front = directed_points_on_line(collar_side_1_back,child_edge_rotation,collar_height)[0]
    collar_side_2_front = directed_points_on_line(between_point,child_edge_rotation,collar_height)[0]

    start_collar_extremes = (collar_side_1_back,collar_side_2_back)
    end_collar_extremes = (collar_side_1_front,collar_side_2_front)
    
    return start_collar_extremes,end_collar_extremes



def draw_double_lined_connection(start_extremes,end_extremes):
    #start: tuple containing start points
    #end: tuple containing end points
    
    global msp,dwg
    msp.add_line(start_extremes[0],end_extremes[0])
    msp.add_line(start_extremes[1],end_extremes[1])
    

def draw_collar_reducer(start_extremes,end_extremes):
    c1,c2,c3,c4 = start_extremes[0],end_extremes[0],end_extremes[1],start_extremes[1]
    msp.add_lwpolyline([c1,c2,c3,c4,c1])
    
def place_block(block_type,node,joint_defaults,conn_width=None):

    #block_obj = joint_defaults.get(block_type,joint_defaults['bend'])
    block_obj = joint_defaults.get(block_type,0)
    if block_obj==0:
        print('NOT FOUND BLOCK')
        return 

    block_name = block_obj['block_name']

    importer = Importer(dwg_joints, dwg)
    importer.import_block(block_name)
    importer.finalize()

    #print(block_name,"BLOCK NAME\n\n")
    offset = block_obj.get('center',ezdxf.math.Vector(0,0,0))
    rotation = node['rotation']
    location = node['shifted_location']
    
    layer = block_name
     
    scale = (conn_width)/75
    place_block_at_location(block_name, location, scale, rotation,
                            offset, layer, msp)
 
    
FACTOR = 1	
def draw(graph,joint_defaults):
#DRAW connection-target_node Pair-wise
    c = 0
    for connection in graph.edges:

        
        connection_obj = graph.edges[connection]

        width = float(graph.edges[connection]['size'].split('x')[0])*FACTOR

        connection_obj['end_trim'] = connection_obj.get('end_trim',0) #*(width/75)
        connection_obj['start_trim'] = connection_obj.get('start_trim',0) #*(width/75)

        source_node,target_node = connection[0],connection[1]
        
        source_obj,target_obj = graph.nodes[source_node],graph.nodes[target_node]
        
        # msp.add_line(source_obj['location'],target_obj['location'])
        # msp.add_circle(target_obj['location'],(50+c)*FACTOR)
        # c += 40
        
        #print(source_obj['vector'],target_obj['vector'])
        #parallel_point = directed_points_on_line(source_obj['connection_point'] ,source_obj['vector'].angle,source_obj['vector'].magnitude)[0]
        #msp.add_circle(source_obj['connection_point'],5,dxfattribs={'color':3})
        
        connection_rotation = find_rotation(source_obj['connection_point'],target_obj['shifted_location'])*(math.pi/180)
        #print(source_obj['location'],connection_rotation,graph.edges[connection]['start_trim']*FACTOR,'DIRECTED FUN PARAMETER')
        scale = (width)/75
        start = directed_points_on_line(source_obj['connection_point'],connection_rotation,connection_obj['start_trim'])[0] #connection's start
        end = directed_points_on_line(target_obj['shifted_location'],connection_rotation,connection_obj['end_trim'])[1] #connection's end
        # __debug_location(start, 'start')
        # __debug_location(end, 'end')
        #msp.add_line(start,end)

        angle_per = find_perpendicular_slope_angle(start,end)
        start_extremes = directed_points_on_line(start,angle_per,width/2)
        end_extremes = directed_points_on_line(end,angle_per,width/2)
        
        # msp.add_circle(end_extremes[0],5*FACTOR,dxfattribs={'color':2})
        # msp.add_circle(end_extremes[1],5*FACTOR,dxfattribs={'color':4})
        draw_double_lined_connection(start_extremes,end_extremes)

        if target_obj['type'] == 'reducer':
            child_node = list(graph.successors(target_node))[0]
            child_obj = graph.nodes[child_node]
            child_edge_obj = graph[target_node][child_node]
            child_edge_width = int(child_edge_obj['size'].split('x')[0])*FACTOR

            reducer_width = (int(child_edge_width-width)/2)*FACTOR
            if target_obj['type'] == 'side-center':
                child_conn_rotation = find_rotation(target_obj['connection_point'],child_obj['shifted_location'])*(math.pi/180)
                
                reducer_right_end = directed_points_on_line(target_obj['shifted_location'],child_conn_rotation,child_edge_obj['start_trim'])[0]
                angle_per = find_perpendicular_slope_angle(target_obj['connection_point'],child_obj['shifted_location'])
                end_extremes_reducer = directed_points_on_line(reducer_right_end,angle_per,child_edge_width/2)[0],directed_points_on_line(reducer_right_end,angle_per,child_edge_width/2)[1]
                start_extremes_reducer = end_extremes

                draw_collar_reducer(start_extremes_reducer,end_extremes_reducer)

            else:
                print("QQQQQQQQQ")
                print('Inside else of side-centre')
                print(f'child_edge_width: {child_edge_width}')
                child_conn_rotation = find_rotation(target_obj['connection_point'],child_obj['shifted_location'])*(math.pi/180)
                
                print('connection_rotation', connection_rotation, 'child_conn_rotation', child_conn_rotation)

                # wo_wala_point = directed_points_on_line(target_obj['shifted_location'], target_obj['vector'].angle, target_obj['vector'].magnitude / 2)[0]
                # wo_wala_point = target_obj['connection_point']
                wo_wala_point = target_obj['shifted_location']
                msp.add_circle(wo_wala_point, 2); msp.add_mtext('wo_walla_point').set_location(wo_wala_point)
                
                left_end_reducer = directed_points_on_line(wo_wala_point,child_conn_rotation,child_edge_obj['start_trim'])[0]
                # left_end_reducer = directed_points_on_line(target_obj['connection_point'],child_conn_rotation,child_edge_obj['start_trim'])[0]
                # msp.add_circle(left_end_reducer, 1, dxfattribs={'color': 1}); msp.add_mtext('left_end_reducer').set_location(left_end_reducer)
                
                child_connection_rotation_perpendicular_angle = find_perpendicular_slope_angle(target_obj['connection_point'], child_obj['shifted_location'])
                end_extremes_reducer = directed_points_on_line(left_end_reducer, angle_per, child_edge_width/2)
                start_extremes_reducer = end_extremes
                # msp.add_circle(start_extremes_reducer[0], 3, dxfattribs={'color': 3}); msp.add_mtext('SER1').set_location(start_extremes_reducer[0])
                # msp.add_circle(start_extremes_reducer[1], 3, dxfattribs={'color': 3}); msp.add_mtext('SER2').set_location(start_extremes_reducer[1])
                
                # msp.add_circle(end_extremes_reducer[0], 3, dxfattribs={'color': 5}); msp.add_mtext('EER1').set_location(end_extremes_reducer[0])
                # msp.add_circle(end_extremes_reducer[1], 3, dxfattribs={'color': 5}); msp.add_mtext('EER2').set_location(end_extremes_reducer[1])
    

                draw_collar_reducer(start_extremes_reducer,end_extremes_reducer)
                dwg.saveas('reducer.dxf')






        if target_obj['type'] == 'bend':
            block_type = 'bend' + ('_mirror' if target_obj['mirror'] == True else '')
            place_block(block_type,target_obj,joint_defaults,width)


        elif target_obj['type'] == 'elbow':
            block_type = 'elbow'+ ('_mirror' if target_obj['mirror'] == True else '')
            place_block(block_type,target_obj,joint_defaults,width)

        elif target_obj['type'] == 't':

            #all desired nodes.
            child_node_1,child_node_2 = list(graph.successors(target_node))[0],list(graph.successors(target_node))[1]
            child_obj_1,child_obj_2 = graph.nodes[child_node_1],graph.nodes[child_node_2]
            parent_node = list(graph.predecessor(target_node))[0]
            parent_obj = graph.nodes[parent_node]


            #all desired edges.
            child_edge_1,child_edge_2 = graph[target_node][child_node_1],graph[target_obj][child_node_2]
            parent_edge = graph[source_node][target_node]

            a1 = find_angle(parent_obj['shifted_location'],target_obj['shifted_location'],child_node_1['shifted_location'])
            a2 = find_angle(parent_obj['shifted_location'],target_obj['shifted_location'],child_node_2['shifted_location'])

            if math.pi/2 - 0.1 < a1 < math.pi/2 + 0.1 or 3*math.pi/2 - 0.1 < a1 < 3*math.pi/2 + 0.1:
                child_90,child_180,child_edge_90 = child_obj_1,child_obj_2,graph.edges[child_edge_1],child_edge_1
            else:
                child_90,child_180 ,child_edge_90 = child_obj_2,child_obj_1,graph.edges[child_edge_2],child_edge_2

            start_collar_extremes,end_collar_extremes = get_collar_points(target_obj,child_90,child_edge_90,connection_rotation,width)
            draw_collar_reducer(start_collar_extremes,end_collar_extremes)

        elif target_obj['type'] == 'cross':
            

            #all desired nodes
            successor_list = list(graph.successors(target_node))
            child_node_1,child_node_2,child_node_3 = successor_list[0],successor_list[1],successor_list[2]
            child_obj_1,child_obj_2,child_obj_3 = graph.nodes[child_node_1],graph.nodes[child_node_2],graph.nodes[child_node_3]
            parent_node = list(graph.predecessors(target_node))[0]
            parent_obj = graph.nodes[parent_node]

            a1 = find_angle(parent_obj['shifted_location'],target_obj['shifted_location'],child_obj_1['shifted_location'])
            a2 = find_angle(parent_obj['shifted_location'],target_obj['shifted_location'],child_obj_2['shifted_location']) 
            a3 = find_angle(parent_obj['shifted_location'],target_obj['shifted_location'],child_obj_3['shifted_location'])

            if math.pi - 0.1 <= a1 <= math.pi + 0.1:
                child_180,child_x_1,child_x_2 = child_obj_1,child_obj_2,child_obj_3
                child_edge_x_1,child_edge_x_2 = graph[target_node][child_node_2],graph[target_node][child_node_3]
            elif math.pi - 0.1 <= a2 <= math.pi + 0.1:
                child_180,child_x_1,child_x_2 = child_obj_2,child_obj_1,child_obj_3
                child_edge_x_1,child_edge_x_2 = graph[target_node][child_node_1],graph[target_node][child_node_3]
            elif math.pi - 0.1 <= a3 <= math.pi + 0.1:
                child_180,child_x_1,child_x_2 = child_obj_3,child_obj_1,child_obj_2
                child_edge_x_1,child_edge_x_2 = graph[target_node][child_node_1],graph[target_node][child_node_2]
            else:
                continue
                child_180,child_x_1,child_x_2 = child_obj_3,child_obj_1,child_obj_2
                child_edge_x_1,child_edge_x_2 = graph[target_node][child_node_1],graph[target_node][child_node_2]


            #left collar
            

            start_collar_extremes,end_collar_extremes = get_collar_points(target_obj,child_x_1,child_edge_x_1,connection_rotation,width)
            draw_collar_reducer(start_collar_extremes,end_collar_extremes)

            #right collar
            start_collar_extremes,end_collar_extremes = get_collar_points(target_obj,child_x_2,child_edge_x_2,connection_rotation,width)
            draw_collar_reducer(start_collar_extremes,end_collar_extremes)
        else:
            print("ADITYA LAST ELSE",connection_obj['start_trim'],connection_obj['end_trim'])
        

def draw_ductings(graph: nx.DiGraph):
    """This function draws ducting from the updated graph

    Args:
        graph (nx.DiGraph): It is the updated through the 'update_graph_properties' function.
    """    
    for node in graph.nodes():
        in_degree = graph.in_degree(node)
        out_degree = graph.out_degree(node)
        
        if out_degree == 1:
            # Draw the Bend or Reducer or Elbow case
            ducting_types = {'bend': draw_bend, 'reducer': draw_reducer, 'elbow': draw_elbow}
        elif out_degree == 2:
            # Draw the 't' or 'special t' cases
            ducting_types = {'t': draw_t, 'special t': draw_special_t}
        elif out_degree == 3:
            # Draw the 'cross' case
            ducting_types = {'cross': draw_cross}
            
    print('Ducting drawings success!')

# Logic:
PRIORITY_LIST = ['CS unit']
def get_ducting(msp, dwg, layer_name: str, conversion_factor, params_dict: dict) -> List[Ducting]:
    data = get_json_object()
    joints_dict = get_joints_dict(data)
    entities_dict = get_entities_dict(data)
    connections = get_connections(data)
    custom_joint_defaults = get_joint_defaults(data)
    graph = get_graph(connections, joints_dict, entities_dict)
    draw_graph(graph)
    directed_graph = get_directed_graph(graph, PRIORITY_LIST)
    
    #draw_graph(directed_graph)
    
    # Have to update graph properties if any
    update_graph_properties(directed_graph, custom_joint_defaults)

    for i in graph.nodes:
        node = graph.nodes[i]
        #print(node.keys())

    clean_other_json_properties(json)
    draw(directed_graph,custom_joint_defaults)
    print(directed_graph.edges,"EDGES of DIgraph")

    for i in directed_graph.nodes:
        n = directed_graph.nodes[i]
        r = 12
        #msp.add_circle(n['location'],r)
        r = 12
        #msp.add_circle(n['shifted_location'],r)

dwg_joints = ezdxf.readfile('setup/'+'joints.dxf')
dwg = ezdxf.readfile('in.dxf')
msp = dwg.modelspace()
get_ducting(msp, None, None, None, None)


dwg.saveas('ducting_drawing.dxf')