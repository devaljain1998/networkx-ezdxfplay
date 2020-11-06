"""This module contains sophisticated functions that are used in processing wall_lines and wall_groups.
In this module we use graphs from networkx to clean the wall_lines irregularities that may have been left by the drafters while creating the dxf file.

Aim: Cleaning the dxf file's walls is really important because due to irregularities we are not able to determine the exact costs.
"""
# IMPORTS:
import networkx as nx
import logging


# Declarations:
logger = logging.getLogger(__name__)


# CODE:
def clean_wall_lines_and_node_edge_count(graph: nx.Graph, wall_lines: list, node_edge_count: dict):
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
    one_edge_count_nodes = node_edge_count.get(1)
    
    # 1. Then loops through all the one-edge-count nodes.
    for node in one_edge_count_nodes:
        # 1.1. then fetch its nearests node to the point:
        nearest_node = get_nearest_node(node)
        # 1.2. loop through all the edges of the nearest_node:
        for edge in graph.edges(nearest_node):
            # 1.2. check if node intersects the edge?
            if (intersection(edge, node)):
                # 1.2.1 If they intersects then break the edge into two parts:
                break_edge_into_two_edges(edge, node)
                update_the_graph_and_node_edge_count(graph, node_edge_count)
    
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
    # 1. Create a network x graph from the lines
    graph = nx.Graph()
    graph.add_edges_from(wall_lines)
    logger.debug('graph initialized.')
    
    # Edge count dictionary for track_record:
    node_edge_count = {}
    
    # 2. Now preprocess the graph by finding out that for how many edges is a node connected with:
    # - To find this we need to iterate the graph from all the nodes.
    # - Keep filling the edge_count of all the node in the dictionary to keep a track-record.
    for node in graph.nodes:
        edge_count = len(list(graph.edges(node)))
        node_set = node_edge_count.get(edge_count, set())
        node_set.insert(node)
        
    # Clean the wall lines and the nodes:
    clean_wall_lines_and_node_edge_count(wall_lines, node_edge_count)
        
    #4. Loop infinitely until no edge remains of edge_count > 2:
    def is_edge_count_greater_than_two_exists(node_edge_count: dict) -> bool:
        """Returns true if there exists keys > 2 in the node_edge_count dictionary"""
        return len(list(filter(lambda key: key > 2, node_edge_count.keys()))) > 0
        
    while (is_edge_count_greater_than_two_exists(node_edge_count)):
        # 4.1 Traverse the nodes with 1-edge connectivity and connect them with the nearest node.
        for edge_count_1_node in edge_count.get(1, []):
            # Connect edge count 1 nodes with the nearest nodes
            # 4.2 Update the connectivity of the node after that.
            connect_to_nearest_node(base_node = edge_count_1_node)
        
        # Now traverse of nodes with edge_count greater than 3:
        edge_counts_of_nodes_greater_than_two = list(filter(lambda key: key > 2, 
                                                            node_edge_count.keys()))
        
        for edge_count in edge_counts_of_nodes_greater_than_two:
            node_set = node_edge_count[edge_count]
            # Traverse node by node and delete the edge with edge_count > 2:
            for node in node_set:
                graph_node = graph.nodes[node]
                edges = graph.edges(node)
                # Now loop through all the edges and delete the edge which has the node with edge_count > 2:
                delete_nodes_with_edge_count_greater_than_two(base_node = node, edges = edges)
        

    new_wall_lines = get_wall_lines_from_graph_edges(graph)

    return new_wall_lines
