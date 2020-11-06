"""
This module will contain functions for calculating the area and the volume of the walls.
That helps in the cost estimation of the project.

The main aim of this module is to automate the cost automation so that we can save tremendous time in between the projects.

Procedure of this module:
[Procedure]
"""

# Imports:
from typing import Tuple
import logging
import networkx as nx


# Declarations: (later will be moved from the file).
class WallGroup(object):
    """This class represents a wall group which is a collection of walls.

    Args:
        object ([type]): [description]
    """
    # Static label number for labeling the walls in the wall group
    label_number = 1
    
    def __init__(self, walls, area=None, height=None, under_the_beam=[None]):
        self.walls = self.__set_walls(walls)
        self.area = area
        self.height = height
        self.under_the_beam = under_the_beam
        
    def __set_walls(self, walls):
        # TODO: This function is to be completed for setting the walls.
        return walls

# Constants:
msp = None
dwg = None
logger = logging.getLogger(__name__)


# Code:
def set_up_cost_estimation_module(*args, **kwargs):
    """
    This function is used to do some hard work before the module's main function can get itself to working.
    Anything that is used to be initialized before we can work on other functions will come here.
    """
    logger.info('Success in setting-up cost estimation.')
    return


def get_columns(msp, column_layer: str) -> List:
    """This function returns the list of columns by grouping them.
    It query's the msp to get all the columns from the layers and them groups the column lines
    after that we are left with the group of columns.

    Args:
        msp : msp of the input dxf file.
        column_layer (str): Name of the column layer in the dxf file.

    Returns:
        List: Returns a list of columns.
    """
    
    def get_columns_from_polylines(msp, column_layer: str) -> List:
        """This function returns the list of columns by which are in polyline form in dxf.

        Args:
            msp : msp of the input dxf file.
            column_layer (str): Name of the column layer in the dxf file.

        Returns:
            List: Returns a list of columns.
        """
        polyline_columns = []
        column_polylines = msp.query(f'LWPOLYLINE[layer=="{column_layer}"]')
        for polyline in column_polylines:
            polyline_columns.append(list(polyline))
        return polyline_columns
    
    columns = []
    # Fetch columns from the polyline:
    column_polyline_points = get_columns_from_polylines(msp= msp, column_layer= column_layer)
    
    # TODO: Fetch columns from lines also (in future).
    
    columns.extend(column_polyline_points)
    return columns


def get_preprocessed_data(identification_json: dict, msp, column_layer: str, *args, **kwargs) -> Tuple["columns, doors, windows"]:
    """This function will return the pre-processed data used in the module.
    Args:
        - identification_json (dict): The identification_json in the dict format.
        - msp: For querying out the Doors, Columns and Windows.
        - column_layer (str): The layer name of the columns.
        
    Returns:
        - columns, doors, windows (tuple): The function will return the columns doors 
                                            and windows fetched from the arguments.
    """
    def get_doors(entities: dict) -> List[dict]:
        """This function returns the doors from the entities of the identification_json.

        Args:
            entities (dict): entities from identification_json.

        Returns:
            List[dict]: Returns a list of door objects.
        """
        doors = list(filter(lambda entity: entity['type'] == 'door', entities))
        return doors
    
    def get_windows(entities: dict) -> List[dict]:
        """This function returns the windows from the entities of the identification_json.

        Args:
            entities (dict): entities from identification_json.

        Returns:
            List[dict]: Returns a list of window objects.
        """
        windows = list(filter(lambda entity: entity['type'] == 'window', entities))
        return windows
    
    # Get entities:
    entities = {entity['number'] : entity for entity in identification_json['entities']}
    
    # Get Doors:
    doors = get_doors(entities)
    logger.debug(f'Doors successfully fetched: {len(doors)}')
    
    # Get Windows:
    windows = get_windows(entities)
    logger.debug(f'Windows successfully fetched: {len(windows)}')
    
    # Get columns:
    columns = get_columns(msp, column_layer)
    logger.debug(f'Columns successfully fetched: {len(columns)}')
    
    logger.info('Successfully got the pre-processed data.')
    return columns, doors, windows


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
        
    #3. Loop infinitely until no edge remains of edge_count > 2:
    def is_edge_count_greater_than_two_exists(node_edge_count: dict) -> bool:
        """Returns true if there exists keys > 2 in the node_edge_count dictionary"""
        return len(list(filter(lambda key: key > 2, node_edge_count.keys()))) > 0
        
    while (is_edge_count_greater_than_two_exists(node_edge_count)):
        # 3.1 Traverse the nodes with 1-edge connectivity and connect them with the nearest node.
        for edge_count_1_node in edge_count.get(1, []):
            # Connect edge count 1 nodes with the nearest nodes
            # 3.2 Update the connectivity of the node after that.
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

def get_detected_wall_groups(msp, wall_layer: str, *args, **kwargs) -> List['WallGroup']:
    """This functions returns list of wall groups are present in the dxf files.
    
    Procedure:
        It does so by querying out all the wall points from the dxf file.
        Then it groups all the individual wall-lines (walls) into groups.
        In the process of grouping the walls it also labels them.

    Args:
        msp: The modelspace of the document from which the walls would be queried.
        wall_layer (str): The name of layer in which the walls are present.

    Returns:
        List['WallGroup']: [description]
    """
    wall_lines = msp.query(f'LINE[layer=={wall_layer}]')
    
    # Cleaning wall lines through networkx (graph theory).
    wall_lines = get_cleaned_wall_lines(wall_lines)
    
    # Creating wall groups:
    

def get_estimated_cost_data(msp, dwg, identification_json: dict, *args, **kwargs):
    """This function gives the data to help in calculating the estimated cost.
    - Procedure of the function:
        [Procedure]
    [Args]
    [Returns]
    """
    # Set module up like constants and some parameters to be used throughout the module
    set_up_cost_estimation_module(*args, **kwargs)
    
    # Get wall groups, columns, door_details and window_details
    columns, doors, windows = get_preprocessed_data(*args, **kwargs)
    
    # Get Wall groups:
    wall_groups = get_detected_wall_groups(msp, *args, **kwargs)
    
    # Extend the wall groups:
    wall_groups = get_extended_wall_groups(wall_groups, *args, **kwargs)
    
    # Now estimate the costs:
    estimated_cost_data = get_estimated_costs(wall_groups, *args, **kwargs)
    
    # If required then process (or beautify) the estimated cost_data
    cleaned_estimated_cost_data = get_cleaned_estimated_cost_data(estimated_cost_data, *args,
                                    **kwargs)
    
    return cleaned_estimated_cost_data