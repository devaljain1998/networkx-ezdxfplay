"""This module contains sophisticated functions that are used in processing wall_lines and wall_groups.
In this module we use graphs from networkx to clean the wall_lines irregularities that may have been left by the drafters while creating the dxf file.

Aim: Cleaning the dxf file's walls is really important because due to irregularities we are not able to determine the exact costs.
"""
# IMPORTS:
import networkx as nx
import logging
from pillarplus.math import get_nearest_points_from_a_point, is_between
from typing import List
import sys
# import matplotlib.pyplot as plt
import ezdxf

# Declarations:
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


# DEBUGGING:
# Through EZDXF:
dwg = ezdxf.new('R2010')
dwg.layers.new('WALL')
msp = dwg.modelspace()
import os
filepath = f'dxfFilesOut/debug_dxf/'
debug_counter = 0

# FURTHER DEBUG:
_dwg = ezdxf.new('R2010')
_dwg.layers.new('WALL_DEBUG')
_msp = _dwg.modelspace()


def __debug_location(point, name: str = 'debug', radius = 2, color:int = 2):
    msp.add_circle(point, radius, dxfattribs={'color': color, 'layer': 'debug'})
    msp.add_mtext(name, dxfattribs = {'layer': 'debug'}).set_location(point)
    
    _msp.add_circle(point, radius, dxfattribs={'color': color, 'layer': 'debug'})
    _msp.add_mtext(name, dxfattribs = {'layer': 'debug'}).set_location(point)
    
def __save_debug_dxf_file():
    global debug_counter
    dwg.saveas(filepath + f'debug_wall_{debug_counter}.dxf')
    print('saved dxf file for debug_no: ', debug_counter)
    debug_counter += 1
    
def __save_graph_debug_dxf_file(wall_lines):
    global debug_counter
    for wall_line in wall_lines:
        _msp.add_line(wall_line[0], wall_line[1], dxfattribs = {'layer': 'WALL_DEBUG'})

    _dwg.saveas(filepath + f'debug_graph_wall_{debug_counter}.dxf')
    print('saved dxf GRAPH file for debug_no: ', debug_counter)

    
def __add_wall_lines(wall_lines):
    for wall_line in wall_lines:
        msp.add_line(wall_line[0], wall_line[1], dxfattribs = {'layer': 'WALL'})
    __save_debug_dxf_file()
    
def __add_graph_wall_lines(wall_lines):
    # REMOVING PREVIOUS LAYERS:
    # TODO: REMOVE
    # for wall_line in wall_lines:
    #     _msp.add_line(wall_line[0], wall_line[1], dxfattribs = {'layer': 'WALL_DEBUG'})
    __save_graph_debug_dxf_file(wall_lines)    

# Through MATPLOTLIB:
# fig_size = plt.rcParams["figure.figsize"]
# fig_size[0] = 100
# fig_size[1] = 80
# plt.rcParams["figure.figsize"] = fig_size


# def draw_graph(directed_graph):
#     global debug_counter
#     plt.figure(figsize =(10,10))
#     nx.draw_networkx(directed_graph)
#     plt.axis('off')
#     plt.tight_layout();
#     plt.savefig(f'dxfFilesOut/debug_graphs/graph_image_{debug_counter}.jpg')
#     debug_counter += 1
#     if debug_counter > 10:
#         print('Now terminating the program')
#         import sys
#         sys.exit(1)


# Helper functions:
def get_nodes_with_degree(degree: int, graph: nx.Graph) -> list:
    """Returns a list of nodes with degree d"""
    return list(filter(lambda node: graph.degree(node) == degree, graph.nodes))


def remove_self_edges_from_the_graph(graph: nx.Graph):
    """Removes self-edges from the graph"""
    graph.remove_edges_from(nx.selfloop_edges(graph))
    print('self-loop edges deleted')

def get_nearest_nodes(node, graph) -> List[tuple]:
    """Function to get the nearest nodes from node in the graph.

    Args:
        node (nx.Node): current node
        graph (nx.Graph): graph

    Returns:
        List[tuple]: list of nearest nodes in decreasing order.
    """
    points = list(graph.nodes(data = False))
    point = node
    node_edge = list(graph.edges(node))[0]
    # Removing the points of node edges so that do not get repeated.
    points.remove(node_edge[0]); points.remove(node_edge[1])
    nearest_points = get_nearest_points_from_a_point(point, points)
    return nearest_points

def intersection(line: List[tuple], point: tuple) -> bool:
    """Function to find whether a point lies on a line or not.

    Args:
        line (List[tuple])
        point (tuple)

    Returns:
        bool: True if point intersects line otherwise False.
    """
    return is_between(point, line[0], line[1])

def break_edge_into_two_edges(edge, node, graph):
    # Fetch points from edge
    p1, p2 = edge
    # Create new edges
    new_edges = [(p1, node), (node, p2)]
    graph.add_edges_from(new_edges)
    # Delete the current edge
    graph.remove_edge(edge[0], edge[1])
    return

def update_the_graph_and_node_edge_count(*args, **kwargs):
    # TODO: complete this function in the most optimized way:
    return

def connect_to_nearest_node(node, graph):
    nearest_node = get_nearest_nodes(node, graph)[0]
    new_edge = (node, nearest_node)
    graph.add_edge(new_edge[0], new_edge[1])
    return

def delete_nodes_with_edge_count_greater_than_two(base_node, edges, graph):    
    # to handle problem:
    edges_to_be_removed = []
    
    # DEBUG:
    print('base_node: ', base_node, 'degree: ', graph.degree(base_node))
    if debug_counter >= 2:
        debug_mode = True
        if base_node == (315820.1279, 6131.6141):
            fishy_mode = True
            
    if graph.degree(base_node) == 2:
        print('This node is not suitable for deletion.')
        return
    
    # now traverse through the edges and remove the edge with the node having greater than one degree
    for edge in edges:
        node = edge[0] if edge[0] != base_node else edge[1]
        # remove this edge if this edge has a degree greater than 2:
        if graph.degree(node) > 2:
            edges_to_be_removed.append((edge[0], edge[1]))
            
    graph.remove_edges_from(edges_to_be_removed)
    logger.debug(f'Edges with (edge_count > 2) successfully deleted for base_node:{base_node}')
    # DEBUG:
    print(f'Edges with (edge_count > 2) successfully deleted for base_node:{base_node}')
    print(f'for edges_to_be_removed:{edges_to_be_removed if edges_to_be_removed != [] else "NONE"}')
    __debug_location(base_node)
    print('after deletion of edges: ', 'base_node: ', base_node, 'degree: ', graph.degree(base_node))
    
    return

def get_wall_lines_from_graph_edges(graph) -> list:
    wall_lines = list(graph.edges)
    return wall_lines


def get_node_edge_count(graph: nx.Graph) -> dict:
    """Function to get the node_edge_count.

    Args:
        graph ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Edge count dictionary for track_record:
    node_edge_count = {}

    # 2. Now preprocess the graph by finding out that for how many edges is a node connected with:
    # - To find this we need to iterate the graph from all the nodes.
    # - Keep filling the edge_count of all the node in the dictionary to keep a track-record.
    for node in graph.nodes:
        edge_count = len(list(graph.edges(node)))
        node_set = node_edge_count.get(edge_count, set())
        node_set.insert(node)
    return node_edge_count

# CODE:
def clean_wall_lines_and_node_edge_count(graph: nx.Graph, wall_lines: list):
    """This function cleans wall_lines and updates node's edge counts accordingly.
    
    Aim:
        The main aim of this function is to remove most of the one edge-nodes before even starting with the main algorithm as much as we can.
    
    Procedure:
        0. Fetch all the one_edge_count nodes.
        1. Then loops through all the one-edge-count nodes.
            for node in one_edge_count_nodes
            1.1. then it grasps it nearests node to the point:
                nearest_node = get_nearest_node(node)
            1.2. loop through all the edges of the nearest_node:
                for edge in graph.edges(nearest_node)
                1.2. check if node intersects the edge?
                    if (intersection(edge, node))
                1.2.1 If they intersects then break the edge into two parts:
                    Example: A-----(B)-----C {Here node B lies between the edge A and C}.
                    We will convert it into: A-----B-----C
                    Code: break_edge_into_two_edges(edge, node)
                    1.2.1.2: update_the_graph_and_node_edge_count

    Args:
        graph (nx.Graph): Graph containing wall_lines end-points as node and wall lines as edges.
        wall_lines (list): List of wall_lines.
        node_edge_count (dict): [description]
    """
    # 0. Fetch all the one_edge_count nodes.
    one_edge_count_nodes = get_nodes_with_degree(1, graph)
    
    # 1. Then loops through all the one-edge-count nodes.
    for node in one_edge_count_nodes:
        # 1.1. then fetch its nearests node to the point:
        nearest_nodes = get_nearest_nodes(node, graph)
        # 1.2. loop through all the edges of the nearest_node:
        for nearest_node in nearest_nodes:
            intersection_flag = False
            for edge in graph.edges(nearest_node):
                # 1.2. check if node intersects the edge?
                if (intersection(edge, node)):
                    # 1.2.1 If they intersects then break the edge into two parts:
                    break_edge_into_two_edges(edge, node, graph)
                    intersection_flag = True
                    break
                
            if intersection_flag: break
    
    return


def get_cleaned_wall_lines(wall_lines: list) -> list:
    """This function will return cleaned wall_lines using networkx.

    Args:
        wall_lines (list): The lines which has come after quering the msp with the wall_layer.
        
    Procedure:
        1. Create a networkx graph from the wall_lines in which individual end-points are the nodes
            and lines are represented as edges.
        2. Now preprocess the graph by finding out that for how many edges is a node connected with:
            - To find this we need to iterate the graph from all the nodes.
            - Keep filling the edge_count of all the node in the dictionary to keep a track-record.
        3. Clean all the edges of edge_count: 1. (Whenever any node occures in-between intersection point of other node then it is needed to break that edge into 2 edges).
            Example: A-----(B)-----C {Here node B lies between the edge A and C}.
            We will convert it into: A-----B-----C
            And then we will be updating the node counts accordingly.
        4. Now we need to loop infinitely untill (Condition: No edges with edge_count > 2 exists in the graph):
        NOTE: This algorithm is based upon the assumtion that eventually every node will be of 2 degree.
            Procedure of algorithm:
            4.1 Traverse the nodes with 1-edge connectivity and connect them with the nearest node.
            4.2 Update the connectivity of the node after that.
            4.3 Now check if nodes with edge_count > 2 exists and if yes then remove the nearest node of them with edge_count > 2.
                4.3.1 NOTE: in the process WE DO NOT NEED TO DELETE THE NODE which was recently connected by the 1-edges node (Otherwise the loop will go in infinite).
                
        5. Finally form line pairs with final edges.
        6. Return the new_wall_lines.

    Returns:
        list: Returns the list of proper wall lines.
    """
    logger.info('Now cleaning wall_lines.')
    print('Now cleaning wall_lines.')
    
    #DEBUG:
    __add_wall_lines(wall_lines)
    
    # 1. Create a network x graph from the lines
    graph = nx.Graph()
    graph.add_edges_from(wall_lines)
    logger.debug('graph initialized.')
    print('graph initialized.')
        
    # Clean the wall lines and the nodes:
    clean_wall_lines_and_node_edge_count(graph, wall_lines)
    
    # DEBUG:
    c_wall_lines = get_wall_lines_from_graph_edges(graph)
    __add_graph_wall_lines(c_wall_lines)
        
    #4. Loop infinitely until no edge remains of edge_count > 2:
    def is_edge_count_greater_than_two_exists(graph) -> bool:
        """Returns true if there exists keys > 2 in the node_edge_count dictionary"""
        return len(list(filter(lambda node: graph.degree(node) > 2, graph.nodes))) > 0
        
    while (is_edge_count_greater_than_two_exists(graph)):
        # DEBUG:
        print('DEBUG_COUNTER:', debug_counter)
        print('Current graph edges: ', len(graph.nodes))
        print('current_wall_lines', len(graph.edges))
        
        # 4.1 Traverse the nodes with 1-edge connectivity and connect them with the nearest node.
        for edge_count_1_node in get_nodes_with_degree(1, graph):
            # Connect edge count 1 nodes with the nearest nodes
            # 4.2 Update the connectivity of the node after that.
            connect_to_nearest_node(node = edge_count_1_node, graph = graph)
                            
        # Now traverse of nodes with edge_count greater than 3:        
        edge_counts_of_nodes_greater_than_two = {degree[1] for degree in graph.degree if degree[1] > 2}
        
        # DEBUG:
        print('Now deleting nodes with edge_count > 2:')
        print('edge_counts_of_nodes_greater_than_two', edge_counts_of_nodes_greater_than_two)
        
        for edge_count in edge_counts_of_nodes_greater_than_two:
            print('\nedge_count:', edge_count)
            node_set = get_nodes_with_degree(edge_count, graph)
            # Traverse node by node and delete the edge with edge_count > 2:
            for node in node_set:
                graph_node = graph.nodes[node]
                edges = graph.edges(node)
                # Now loop through all the edges and delete the edge which has the node with edge_count > 2:
                delete_nodes_with_edge_count_greater_than_two(
                    base_node = node, edges = edges, graph = graph)
                
        print('Nodes with edge_count > 2 fixed for this cycle.')
        # print('Now removing self-edges:')
        # remove_self_edges_from_the_graph(graph)
                
        # DEBUG SPECIAL NODE
        print('special_node:', graph.degree((315038.6279144774, 6194.614122894351))) #315038.6279144774, 6194.614122894389
                
        print('One cycle complete', debug_counter, '\n')
        # DEBUG:
        __save_debug_dxf_file()
        
        current_wall_lines = get_wall_lines_from_graph_edges(graph)
        if debug_counter == 0:
            __add_graph_wall_lines(current_wall_lines)
        else:
            __save_graph_debug_dxf_file(current_wall_lines)
        if not debug_counter <= 4:
            print('Now terminating')
            break #sys.exit(1)
        print()
        # draw_graph(graph)
        
    # DEBUG:
    from pprint import pprint
    graph_nodes = list(graph.nodes)
    graph_nodes.sort()
    print('Printing graph nodes')
    pprint(graph_nodes)
    
    new_wall_lines = get_wall_lines_from_graph_edges(graph)

    return new_wall_lines
