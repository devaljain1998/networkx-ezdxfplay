import networkx as nx
from pillarplus.math import find_centroid_2d, find_mid_point

def __debug_location(msp, point, name: str = 'debug', radius = 2, color:int = 2):
    msp.add_circle(point, radius, dxfattribs={'color': color, 'layer': 'debug'})
    msp.add_mtext(name, dxfattribs = {'layer': 'debug'}).set_location(point)

def get_connected_graph_components(graph):
    """This function returns connected components from the graph"""
    return [graph.subgraph(component_set) for component_set in nx.connected_components(graph)]

def label_component_edges(msp, edges, component_number):
    for edge in edges:
        edge_mid_point = find_mid_point(edge[0], edge[1])
        msp.add_mtext(f'{component_number}', dxfattribs = {'layer' : 'comp_debug_text'}).set_location(edge_mid_point)

def draw_components(wall_lines, msp, dwg):
    # 1. Create a network x graph from the lines
    graph = nx.Graph()
    graph.add_edges_from(wall_lines)
    graph_components = get_connected_graph_components(graph)
    # draw centeroids:
    component_number = 1
    for graph_component in graph_components:
        centroid = find_centroid_2d(graph_component.nodes)
        __debug_location(msp, centroid, f'comp{component_number}', 3, 5)
        label_component_edges(msp, graph_component.edges, component_number)
        component_number += 1