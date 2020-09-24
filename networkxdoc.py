# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:57:02 2019

@author: namankasliwal
"""

import networkx as nx
import matplotlib.pyplot as plt


class Entity:

    def __init__(self, point, entType):
        self.point = point
        self.entType = entType

# Directed graphs
G = nx.DiGraph()

e1 = Entity((2, 2), 'Shaft')
e2 = Entity((2, 8), 'FT 2')
e3 = Entity((2, 5), 'FT 3')
e4 = Entity((7, 5), 'FT 4')
e5 = Entity((9, 5), 'FT 5')

# Adding nodes
G.add_node(e1, pos=e1.point, entType=e1.entType)
G.add_node(e2, pos=e2.point, entType=e2.entType)
G.add_node(e3, pos=e3.point, entType=e3.entType)
G.add_node(e4, pos=e4.point, entType=e4.entType)
G.add_node(e5, pos=e5.point, entType=e5.entType)

# Adding edges
G.add_edge(e1, e2, weight='110')
G.add_edge(e3, e4, weight='110')
G.add_edge(e4, e5, weight='110')

# Add e3 in between e1 and e2


def add_node_in_between(e3, e1, e2):
    main_weight = G.edges[e1, e2]['weight']
    G.remove_edge(e1, e2)
    G.add_edge(e1, e3, weight=main_weight)
    G.add_edge(e3, e2, weight=main_weight)

add_node_in_between(e3, e1, e2)

# Traverse through the graph
print('DFS Graph traversal::')
dfs = list(nx.edge_dfs(nx.DiGraph(G.edges), G.nodes))
for u, v in dfs:
    print(u.entType, v.entType)
print('Graph successfully traveresed::\n\n')

# Plot
plt.figure(figsize=(9, 9))
pos = nx.get_node_attributes(G, 'pos')
labels = nx.get_node_attributes(G, 'entType')
nx.draw_networkx(G, pos, with_labels=True, node_color='yellow', labels=labels)
weights = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
plt.show()

# Print details
print("Total number of nodes: ", int(G.number_of_nodes()))
print("Total number of edges: ", int(G.number_of_edges()))

# https://networkx.github.io/documentation/stable/reference/readwrite/json_graph.html
# Graph to JSON - serialize
# Convert graph to dict, it still has objects as items, if any
dict_dump = nx.node_link_data(G)
print('dict_dump', type(dict_dump), dict_dump)

import json
# Convert graph dict to string, while converting all objects also
json_dump = json.dumps(dict_dump, default=lambda o: o.__dict__, indent=4)
print('json_dump', type(json_dump), json_dump)

# Graph from JSON - deserialize
# dict_dump from json_dump
# TO DO

G = nx.node_link_graph(dict_dump, directed=True)

plt.figure(figsize=(9, 9))
pos = nx.get_node_attributes(G, 'pos')
labels = nx.get_node_attributes(G, 'entType')
nx.draw_networkx(G, pos, with_labels=True, node_color='yellow', labels=labels)
weights = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
plt.show()
