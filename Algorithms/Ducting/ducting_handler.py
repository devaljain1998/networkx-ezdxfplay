from typing import List, Dict
import networkx as nx
import json
import matplotlib.pyplot as plt
import math
from pillarplus.math import is_inverted, find_angle, find_rotation

# Constants:
SERVICE_NAME: str = 'ducting'


# Containers
class Ducting:
    def __init__(self, number):
        self.number = number


def get_json_object():
    input_file_path = '/home/deval/Projects/PillarPlus/Study/Algorithms/Ducting/input/'
    input_file_name = 'updated_identification.json'
    with open(input_file_path + input_file_name) as f:
        data = json.load(f)
        print(
            f'Json File: {input_file_name} read success! at {input_file_path}')
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
        key = joint_default['type'] + '_mirror' if joint_default['mirror'] else ''
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
            joint_default_key = graph.nodes[node]['type'] + mirror if graph.nodes['mirror'] else ''
            # Fetching joint default from key
            joint_default = joint_defaults[joint_default_key]
            intrim = joint_default.get('intrim', 0)
            outtrim = joint_default.get('outtrim', 0)
            
            # Now finding the start and out trims of each edges
            parent_edge['end_trim'] = intrim
            child_edge['start_trim'] = outtrim
            
        elif graph.nodes[node]['type'] == 'reducer':
            # finding parent and child nodes
            parent_node = list(graph.predecessors(node))[0]
            child_node = list(graph.successors(node))[0]
            
            # finding parent and child edges
            parent_edge = graph[parent_node][node]
            child_edge = graph[node][child_node]
            
            # Calculating the intrim and outtrim
            width_of_parent_edge = parent_edge['size'].split()
            width_of_reducer = None
            
            
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
            
            def get_outtrim():
                width = float(parent_edge['size'].split('x')[1])
                return width
            outtrim = get_outtrim()
            
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
            
            def get_outtrim():
                width = float(parent_edge['size'].split('x')[1])
                return width
            outtrim = get_outtrim()

            # Finding child_edges and modifying the outtrim if they are perpendicular 
            for child_node in child_nodes:
                to_point = graph.nodes[child_node]['location']
                angle = find_angle(from_point, point, to_point)
                
                if (math.pi/2 - 0.1 < angle < math.pi/2 + 0.1) or (3*math.pi/2 - 0.1 < angle < 3*math.pi/2 + 0.1):
                    child_edge = graph[node][child_node]
                    child_edge['start_trim'] = outtrim
                else:
                    child_edge['start_trim'] = 0


def update_graph_properties(graph: nx.DiGraph, joint_defaults: dict):
    """The function is used to update the graph properties for ease in drawing the ducting.
    This functions is used to update the following properties: 'size', 'rotation', 'type' and 'mirror', 'start_trim' and 'end_trim'.

    Args:
        graph (nx.DiGraph): [description]
        joint_defaults (dict): [description]
    """
    mirror = '_mirror'
    DEFAULT_SIZE = 75
    
    # Traversing the nodes to decide the type of joints:
    for node in graph.nodes():
        in_degree = graph.in_degree(node)
        # Validating in_degree:
        if in_degree > 1:
            raise ValueError(f'Exception: "in_degree" cannot be more than one in ducting. Exception occured in node: {node}')
        
        out_degree = graph.out_degree(node)
        
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
                graph.nodes[node]['mirror'] = is_mirror

                # Finding angle in between the three points
                angle = find_angle(from_point, point, to_point)
                if math.pi/2 - 0.1 < angle < math.pi/2 + 0.1 or 3*math.pi/2 - 0.1 < angle < 3*math.pi/2 + 0.1:
					graph.nodes[node]['type'] = 'bend'
                else:
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
                
                if math.pi - 0.1 < angle1 < math.pi + 0.1:
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
        return


def clean_other_json_properties(json):
    pass


def draw_graph(directed_graph):
    plt.figure(figsize =(10,10))
    nx.draw_networkx(directed_graph)
    plt.axis('off')
    plt.tight_layout();
    plt.savefig('dxfFilesOut/debug_graphs/graph_image.jpg')

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
    directed_graph = get_directed_graph(graph, PRIORITY_LIST)
    
    draw_graph(directed_graph)
    
    # Have to update graph properties if any
    update_graph_properties(graph, joint_defaults)
    clean_other_json_properties(json)
    draw_ductings(graph)

get_ducting(None, None, None, None, None)